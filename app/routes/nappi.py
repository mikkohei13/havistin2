from flask import Blueprint, jsonify, redirect, render_template, request, session
from openai import OpenAI
import app_secrets
import json
import re
import io
import sys
import traceback

nappi_bp = Blueprint("nappi", __name__, url_prefix="/nappi")

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
    "Analysoi tämä suomenkielinen litterointi joka kuvailee lintuhavaintoa, jossa on tyypillisesti lintulajin suomenkielinen nimi, lukumäärä ja muuta tietoa havainnosta.
    
    Palauta ainoastaan JSON-objekti, jossa on seuraavat kentät. Ei markdownia, ei muuta tekstiä.
    - species (suomenkielinen lajinimi merkkijonona, arvaa tarvittaessa)
    - count (kokonaisluku tai tyhjä merkkijono)
    - notes (lyhyt lisähuomio merkkijonona tai tyhjä)
"""



@nappi_bp.route("")
@nappi_bp.route("/")
def nappi_root():
    user_data = session.get("user_data")
    if user_data is None or "errorCode" in user_data:
        return redirect("/login/start")
    return render_template("nappi.html")


def _unauthorized():
    return jsonify({"error_code": "unauthorized", "message": "Kirjaudu ensin sisaan."}), 401


def _normalize_count(value):
    if value is None or value == "":
        return ""
    try:
        return int(value)
    except (TypeError, ValueError):
        return ""


def _extract_json_object(raw_text):
    stripped = raw_text.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped
    match = re.search(r"\{[\s\S]*\}", stripped)
    if match:
        return match.group(0)
    return "{}"


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


def _log_nappi_error(context, error, extra=None):
    print(f"Nappi error [{context}]: {type(error).__name__}: {str(error)}", file=sys.stdout)
    if extra is not None:
        print(f"Nappi error context [{context}]: {extra}", file=sys.stdout)
    print(traceback.format_exc(), sep="\n", file=sys.stdout)


@nappi_bp.route("/api/transcribe", methods=["POST"])
def nappi_transcribe():
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
            "Nappi transcribe request: "
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
        _log_nappi_error(
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
            "Nappi GPT request: "
            f"gpt_model={GPT_MODEL}, "
            f"transcript_chars={len(raw_transcript)}",
            file=sys.stdout,
        )
        completion = client.chat.completions.create(
            model=GPT_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": GPT_SYSTEM_PROMPT},
                {"role": "user", "content": raw_transcript},
            ],
        )
        content = completion.choices[0].message.content or "{}"
        parsed = json.loads(_extract_json_object(content))
        normalized = _normalize_observation(parsed)
    except Exception as error:
        _log_nappi_error(
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
