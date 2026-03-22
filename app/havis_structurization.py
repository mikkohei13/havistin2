"""HAVIS: transcript → species hint + GPT structured observation (shared by API and CLI)."""

import sys
from pathlib import Path

# When run as `python app/havis_structurization.py`, only `app/` is on sys.path; add project root
# so `import app.routes...` works (same layout as `python -m app.havis_structurization`).
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import json
import os
import unicodedata
from typing import Any, Optional

from openai import OpenAI
from pydantic import BaseModel, Field

from app.routes.havis_species_names import SPECIES_NAMES

GPT_MODEL = "gpt-5.4"

SPECIES_MAX_EDIT_FRACTION = 0.3

GPT_SYSTEM_PROMPT = """
Tehtäväsi on muuntaa suomenkielinen lintuhavaintoa kuvaava puheentunnistusteksti rakenteiseksi tiedoksi.

Syöte on epämuodollista puhekieltä ja voi sisältää:
- puheentunnistuksen virheitä, erityisesti lajien nimissä
- katkonaisia tai puhekielisiä ilmauksia
- lukumääriä sanoina tai numeroina
- epätäydellisiä havaintokuvauksia

Jos syötteessä on mukana myös ensimmäisen sanan lajiehdotus, käsittele sitä heikkona vihjeenä. Hyödynnä sitä vain, jos se sopii hyvin muun tekstin asiayhteyteen.

Palauta vain tiedot, jotka ovat kohtuullisen varmasti pääteltävissä tekstistä. Älä keksi puuttuvia tietoja.

Säännöt:

1. Laji
- Tunnista havaittu lintulaji ja palauta sen vakiintunut suomenkielinen nimi oikeinkirjoitettuna.
- Korjaa ilmeiset puheentunnistus- ja kirjoitusvirheet.
- Jos lajia ei voi päätellä, palauta tyhjä merkkijono.
- Älä tarkenna ylätason ryhmää yksittäiseksi lajiksi ilman selvää perustetta.
  Esimerkiksi jos tekstistä ilmenee vain "lokki", palauta "lokki", ei tiettyä lokkilajia.

2. Määrä
- Palauta yksilömäärä kokonaislukuna, jos se ilmenee tekstistä.
- Jos tekstissä on vaihteluväli tai arvio, palauta vähimmäismäärä.
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
            "Havaittujen yksilöiden vähimmäismäärä kokonaislukuna. "
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


def _normalize_count(value: Any):
    if value is None or value == "":
        return ""
    try:
        return int(value)
    except (TypeError, ValueError):
        return ""


def _normalize_observation(data: dict) -> dict:
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


def _is_first_word_break_char(char: str) -> bool:
    if char.isspace():
        return True
    if len(char) != 1:
        return True
    return unicodedata.category(char)[0] == "P"


def _extract_first_word(text: str) -> str:
    text = text.strip()
    if not text:
        return ""
    out = []
    for char in text:
        if _is_first_word_break_char(char):
            break
        out.append(char)
    return "".join(out)


def _levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    la, lb = len(a), len(b)
    if la == 0:
        return lb
    if lb == 0:
        return la
    prev = list(range(lb + 1))
    for i, ca in enumerate(a, start=1):
        cur = [i]
        for j, cb in enumerate(b, start=1):
            ins, delete, sub = cur[j - 1] + 1, prev[j] + 1, prev[j - 1] + (ca != cb)
            cur.append(min(ins, delete, sub))
        prev = cur
    return prev[-1]


def _log_first_word_species_match(
    first_word_display: str,
    closest_match: Optional[str],
    distance: Optional[int],
    suggestion: str,
) -> None:
    print(
        "Havis first_word_species: "
        f"first_word={first_word_display!r} "
        f"closest_match={closest_match!r} "
        f"distance={distance} "
        f"suggestion={suggestion!r}",
        file=sys.stdout,
        flush=True,
    )


def _first_word_species_suggestion(raw_transcript: str) -> str:
    first_word_raw = _extract_first_word(raw_transcript)
    first_word = first_word_raw.casefold()
    if not first_word:
        _log_first_word_species_match(first_word_raw, None, None, "")
        return ""
    best_name = None
    best_d = None
    for species in SPECIES_NAMES:
        d = _levenshtein(first_word, species.casefold())
        if best_d is None or d < best_d:
            best_d = d
            best_name = species
    lens = max(len(first_word), len(best_name))
    if lens == 0:
        _log_first_word_species_match(first_word_raw, best_name, best_d, "")
        return ""
    scale = 1000
    max_dist_scaled = int(round(SPECIES_MAX_EDIT_FRACTION * scale))
    if best_d * scale >= max_dist_scaled * lens:
        _log_first_word_species_match(first_word_raw, best_name, best_d, "")
        return ""
    _log_first_word_species_match(first_word_raw, best_name, best_d, best_name)
    return best_name


def _havis_user_prompt(raw_transcript: str, species_suggestion: str) -> str:
    def esc(s: str) -> str:
        return s.replace("\\", "\\\\").replace('"', '\\"')

    return (
        f'Transkriptio: "{esc(raw_transcript)}"\n'
        f'Ensimmäisen sanan lajiehdotus: "{esc(species_suggestion)}"'
    )


def structurize_transcript(raw_transcript: str, client: OpenAI) -> dict:
    """
    Run species first-word hint + GPT parse. Returns the same shape as /havis/api/transcribe JSON body.
    Raises on API/parse errors.
    """
    raw_transcript = raw_transcript.strip()
    if raw_transcript == "":
        raise ValueError("raw_transcript is empty")

    species_suggestion = _first_word_species_suggestion(raw_transcript)
    user_prompt = _havis_user_prompt(raw_transcript, species_suggestion)

    completion = client.beta.chat.completions.parse(
        model=GPT_MODEL,
        messages=[
            {"role": "system", "content": GPT_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
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
    return {
        "species": normalized["species"],
        "count": normalized["count"],
        "notes": normalized["notes"],
        "raw_transcript": raw_transcript,
        "warnings": normalized["warnings"],
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python app/havis_structurization.py "<transcript text>"', file=sys.stderr)
        sys.exit(1)
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("error: OPENAI_API_KEY is not set", file=sys.stderr)
        sys.exit(1)
    client = OpenAI(api_key=api_key)
    result = structurize_transcript(sys.argv[1], client=client)
    print(json.dumps(result, ensure_ascii=False, indent=2))
