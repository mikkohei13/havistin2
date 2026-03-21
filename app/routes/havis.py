import io
import sys
import traceback
from typing import Optional

from flask import Blueprint, jsonify, redirect, render_template, request, session
from openai import OpenAI
from pydantic import BaseModel, Field

import app_secrets

havis_bp = Blueprint("havis", __name__, url_prefix="/havis")

TRANSCRIBE_MODEL = "gpt-4o-transcribe"
GPT_MODEL = "gpt-5.4"

ALLOWED_AUDIO_TYPES = {
    "audio/mpeg",
    "audio/mp3",
    "audio/mp4",
    "audio/x-m4a",
    "audio/m4a",
    "audio/wav",
    "audio/webm",
    "audio/ogg",
    "application/ogg",
    "video/webm",
}

GPT_SYSTEM_PROMPT = """
Tehtäväsi on muuntaa suomenkielinen lintuhavaintoa kuvaava puheentunnistusteksti rakenteiseksi tiedoksi.

Syöte on epämuodollista puhekieltä ja voi sisältää:
- puheentunnistuksen virheitä, erityisesti lajien nimissä
- katkonaisia tai puhekielisiä ilmauksia
- lukumääriä sanoina tai numeroina
- epätäydellisiä havaintokuvauksia

Palauta vain tiedot, jotka ovat kohtuullisen varmasti pääteltävissä tekstistä.
Älä keksi puuttuvia tietoja.

Säännöt:

1. Laji
- Tunnista havaittu lintulaji ja palauta sen vakiintunut suomenkielinen nimi oikeinkirjoitettuna.
- Korjaa ilmeiset puheentunnistus- ja kirjoitusvirheet.
- Jos lajia ei voi päätellä, palauta tyhjä merkkijono.
- Älä tarkenna ylätason ryhmää yksittäiseksi lajiksi ilman selvää perustetta.
  Esimerkiksi jos tekstistä ilmenee vain "lokki", palauta "lokki", ei tiettyä lokkilajia.

2. Määrä
- Palauta yksilömäärä kokonaislukuna, jos se ilmenee tekstistä.
- Jos tekstissä kuvaillaan selvästi yksi lintu mutta määrää ei sanota erikseen, käytä arvoa 1.
- Jos määrä on epämääräinen tai epäselvä, palauta null.

3. Lisätiedot
- Kirjoita lyhyt suomenkielinen huomio vain tekstissä mainituista lisätiedoista, kuten paikasta, käyttäytymisestä, suunnasta, ajasta, iästä, puvusta tai säästä.
- Älä toista lajia tai määrää ilman tarvetta.
- Jos lisätietoja ei ole, palauta tyhjä merkkijono.

4. Ei-havainto
- Jos teksti ei kuvaa lintuhavaintoa, palauta:
  - species = ""
  - count = null
  - notes = ""

5. Epävarmuus
- Jos puhuja arvelee, kyselee tai epäröi eikä havaintoa voi tulkita riittävän varmasti, suosi tyhjää lajia ja null-arvoja mieluummin kuin arvausta.

6. Useat lajit
- Jos tekstissä mainitaan useita eri lajeja, palauta vain ensimmäinen selvästi havaittu laji siihen liittyvine tietoineen.
- Älä yhdistä useiden lajien määriä samaan havaintoon.
"""


class BirdObservationLLM(BaseModel):
    species: str = Field(
        default="",
        description=(
            "Havaitun linnun vakiintunut suomenkielinen lajinimi oikeinkirjoitettuna. "
            "Jos lajia ei voi tunnistaa riittävän varmasti, palauta tyhjä merkkijono."
        ),
    )
    count: Optional[int] = Field(
        default=None,
        description=(
            "Havaittujen yksilöiden määrä kokonaislukuna. "
            "Käytä arvoa 1, jos tekstissä kuvataan selvästi yksi lintu ilman erikseen mainittua määrää. "
            "Palauta null, jos määrä on epäselvä, epämääräinen tai vain arvioitu."
        ),
    )
    notes: str = Field(
        default="",
        description=(
            "Lyhyt suomenkielinen lisähuomio vain tekstissä mainituista yksityiskohdista, "
            "esimerkiksi paikasta, käyttäytymisestä, suunnasta, iästä, puvusta, ajasta tai säästä. "
            "Palauta tyhjä merkkijono, jos lisätietoja ei ole."
        ),
    )




@havis_bp.route("")
@havis_bp.route("/")
def havis_root():
    user_data = session.get("user_data")
    if user_data is None or "errorCode" in user_data:
        return redirect("/login/start")
    havis_user_id = user_data.get("id")
    if havis_user_id is not None:
        havis_user_id = str(havis_user_id)
    else:
        havis_user_id = ""
    return render_template("havis.html", havis_user_id=havis_user_id)


def _unauthorized():
    return jsonify({"error_code": "unauthorized", "message": "Kirjaudu ensin sisaan."}), 401


def _normalize_count(value):
    if value is None or value == "":
        return ""
    try:
        return int(value)
    except (TypeError, ValueError):
        return ""


def _normalize_observation(data):
    species = data.get("species")
    notes = data.get("notes")
    count = _normalize_count(data.get("count"))

    if not isinstance(species, str):
        species = ""
    if not isinstance(notes, str):
        notes = ""

    species = species.strip()
    notes = notes.strip()
    warnings = []
    if species == "":
        warnings.append("species_unrecognized")

    return {
        "species": species,
        "count": count,
        "notes": notes,
        "warnings": warnings,
    }


def _log_havis_error(context, error, extra=None):
    print(f"Havis error [{context}]: {type(error).__name__}: {str(error)}", file=sys.stdout)
    if extra is not None:
        print(f"Havis error context [{context}]: {extra}", file=sys.stdout)
    print(traceback.format_exc(), sep="\n", file=sys.stdout)


@havis_bp.route("/api/transcribe", methods=["POST"])
def havis_transcribe():
    user_data = session.get("user_data")
    if user_data is None or "errorCode" in user_data:
        return _unauthorized()

    audio = request.files.get("audio")
    if audio is None or audio.filename is None or audio.filename.strip() == "":
        return jsonify({"error_code": "bad_request", "message": "Audio puuttuu."}), 400

    if audio.mimetype and audio.mimetype not in ALLOWED_AUDIO_TYPES:
        return jsonify({"error_code": "bad_request", "message": "Audioformaatti ei ole tuettu."}), 400

    lat_raw = request.form.get("lat", "").strip()
    lng_raw = request.form.get("lng", "").strip()

    for value, field_name in ((lat_raw, "lat"), (lng_raw, "lng")):
        if value == "":
            continue
        try:
            float(value)
        except ValueError:
            return jsonify({"error_code": "bad_request", "message": f"{field_name} ei ole numero."}), 400

    client = OpenAI(api_key=app_secrets.openai_api_key)

    try:
        audio_bytes = audio.read()
        if len(audio_bytes) > 25 * 1024 * 1024:
            return jsonify({"error_code": "bad_request", "message": "Audio on liian suuri (max 25 MB)."}), 400
        audio_buffer = io.BytesIO(audio_bytes)
        audio_buffer.name = audio.filename or "recording.webm"
        print(
            "Havis transcribe request: "
            f"filename={audio_buffer.name}, "
            f"mimetype={audio.mimetype}, "
            f"bytes={len(audio_bytes)}, "
            f"lat={lat_raw or '-'}, lng={lng_raw or '-'}, "
            f"transcribe_model={TRANSCRIBE_MODEL}",
            file=sys.stdout,
        )
        transcription = client.audio.transcriptions.create(
            model=TRANSCRIBE_MODEL,
            file=audio_buffer,
            language="fi",
            response_format="text",
        )
        raw_transcript = transcription.strip()
    except Exception as error:
        _log_havis_error(
            "transcription",
            error,
            extra={
                "filename": audio.filename,
                "mimetype": audio.mimetype,
                "lat": lat_raw,
                "lng": lng_raw,
                "transcribe_model": TRANSCRIBE_MODEL,
            },
        )
        return jsonify({"error_code": "transcription_failed", "message": "Puheen tekstiksi muunnos epaonnistui."}), 502

    if raw_transcript == "":
        return jsonify({"error_code": "transcription_failed", "message": "Tyhja litterointi."}), 502

    try:
        print(
            "Havis GPT request: "
            f"gpt_model={GPT_MODEL}, "
            f"transcript_chars={len(raw_transcript)}",
            file=sys.stdout,
        )
        completion = client.beta.chat.completions.parse(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": GPT_SYSTEM_PROMPT},
                {"role": "user", "content": raw_transcript},
            ],
            response_format=BirdObservationLLM,
        )
        message = completion.choices[0].message
        if message.refusal:
            raise ValueError(f"model_refusal: {message.refusal}")
        if completion.choices[0].finish_reason == "length":
            raise ValueError("incomplete_response_max_tokens")
        if message.parsed is None:
            raise ValueError("parsed_output_missing")
        normalized = _normalize_observation(message.parsed.model_dump())
    except Exception as error:
        _log_havis_error(
            "structured_output",
            error,
            extra={
                "gpt_model": GPT_MODEL,
                "transcript_chars": len(raw_transcript),
            },
        )
        return jsonify({"error_code": "structured_output_invalid", "message": "Tekstin analysointi epaonnistui."}), 502

    return jsonify(
        {
            "species": normalized["species"],
            "count": normalized["count"],
            "notes": normalized["notes"],
            "raw_transcript": raw_transcript,
            "warnings": normalized["warnings"],
        }
    )
