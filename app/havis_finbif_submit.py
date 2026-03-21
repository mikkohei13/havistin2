"""Build FinBIF store-documents from Havis sessions and submit via /documents/validate + /documents."""

from __future__ import annotations

import json
import sys
import traceback
import urllib.parse
from typing import Any, Optional

from helpers import common_helpers

# Vihko (laji.fi notebook) — fixed for Havis submissions
FINBIF_COLLECTION_ID = "HR.1747"
FINBIF_FORM_ID = "JX.519"


def _log_info(message: str, **kwargs: Any) -> None:
    """Structured info line for successful steps and progress (stdout / server logs)."""
    if kwargs:
        try:
            extra = json.dumps(kwargs, ensure_ascii=False, default=str)
        except TypeError:
            extra = repr(kwargs)
        print(f"Havis FinBIF info: {message} | {extra}", file=sys.stdout)
    else:
        print(f"Havis FinBIF info: {message}", file=sys.stdout)


def _log(context: str, err: BaseException, extra: Optional[dict] = None) -> None:
    print(f"Havis FinBIF [{context}]: {type(err).__name__}: {err}", file=sys.stdout)
    if extra:
        print(f"Havis FinBIF context [{context}]: {extra}", file=sys.stdout)
    print(traceback.format_exc(), file=sys.stdout)


def _log_finbif_response(endpoint: str, status: int, body: Any) -> None:
    """Log full FinBIF JSON response for debugging (validate/create errors)."""
    try:
        text = json.dumps(body, ensure_ascii=False, indent=2, default=str)
    except TypeError:
        text = repr(body)
    print(f"Havis FinBIF {endpoint} HTTP {status}:\n{text}", file=sys.stdout)


def _log_submitted_document(doc: dict, label: str = "submitted document") -> None:
    """Log the document payload (truncated if huge)."""
    try:
        text = json.dumps(doc, ensure_ascii=False, indent=2, default=str)
    except TypeError:
        text = repr(doc)
    max_len = 120_000
    if len(text) > max_len:
        text = text[:max_len] + "\n... [truncated]"
    print(f"Havis FinBIF {label} (JSON):\n{text}", file=sys.stdout)


def _pick_taxon_id(results: list, vernacular_fi: str) -> Optional[str]:
    target = vernacular_fi.strip().lower()
    candidates = []
    for r in results:
        tid = r.get("id")
        if not tid or not str(tid).startswith("MX."):
            continue
        candidates.append(r)
    if not candidates:
        return None
    for r in candidates:
        vn = (r.get("vernacularName") or "").strip().lower()
        if vn == target:
            return str(r["id"])
    return str(candidates[0]["id"])


def resolve_taxon_qname(
    vernacular_fi: str, cache: dict[str, str], person_token: Optional[str] = None
) -> Optional[str]:
    key = vernacular_fi.strip().lower()
    if key in cache:
        return cache[key]
    q = urllib.parse.urlencode(
        {
            "query": vernacular_fi.strip(),
            "limit": 12,
            "finnish": "true",
            "species": "true",
            "languages": "fi",
            "matchType": "exact,partial",
            "page": 1,
            "lang": "fi",
        }
    )
    url = f"https://api.laji.fi/autocomplete/taxa?{q}"
    try:
        data = common_helpers.fetch_finbif_api(url, person_token=person_token)
    except Exception as exc:
        _log("resolve_taxon_qname", exc, extra={"query": vernacular_fi})
        return None

    results = data.get("results")
    if results is None and isinstance(data, list):
        results = data
    if not isinstance(results, list):
        results = []
    picked = _pick_taxon_id(results, vernacular_fi)
    if picked:
        cache[key] = picked
    return picked


def _taxon_uri(qname: str) -> str:
    if qname.startswith("http://"):
        return qname
    return f"http://tun.fi/{qname}"


def _parse_float(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _observation_count(obs: dict) -> int:
    raw = obs.get("count")
    if raw is None or raw == "":
        return 1
    try:
        n = int(raw)
        return max(1, n)
    except (TypeError, ValueError):
        return 1


def _unit_notes(obs: dict) -> str:
    """Muistiinpanot field only; omit notes in payload when empty."""
    n = obs.get("notes")
    if n is None or str(n).strip() == "":
        return ""
    return str(n).strip()


def _observer_leg_identifier(user_data: dict) -> str:
    """FinBIF /person `id` (e.g. MAN.xxx) for gatheringEvent.leg."""
    pid = user_data.get("id")
    if pid is None:
        return ""
    return str(pid).strip()


def _gathering_center_coords(observations: list[dict]) -> tuple[Optional[float], Optional[float]]:
    lats = []
    lngs = []
    for obs in observations:
        lat = _parse_float(obs.get("lat"))
        lng = _parse_float(obs.get("lng"))
        if lat is not None and lng is not None:
            lats.append(lat)
            lngs.append(lng)
    if not lats:
        return None, None
    return sum(lats) / len(lats), sum(lngs) / len(lngs)


def _gathering_geometry_from_observations(observations: list[dict]) -> dict[str, Any]:
    """
    GeoJSON for the gathering: one Point if a single location, else a Polygon
    bounding box over all unit coordinates.
    """
    lngs: list[float] = []
    lats: list[float] = []
    for obs in observations:
        lat = _parse_float(obs.get("lat"))
        lng = _parse_float(obs.get("lng"))
        if lat is not None and lng is not None:
            lngs.append(lng)
            lats.append(lat)
    if not lngs:
        raise ValueError("Ei koordinaatteja geometriaa varten.")

    if len(lngs) == 1:
        return {"type": "Point", "coordinates": [lngs[0], lats[0]]}

    min_lng, max_lng = min(lngs), max(lngs)
    min_lat, max_lat = min(lats), max(lats)
    if min_lng == max_lng and min_lat == max_lat:
        return {"type": "Point", "coordinates": [min_lng, min_lat]}

    # Closed ring: SW, SE, NE, NW, SW (GeoJSON lon, lat)
    ring = [
        [min_lng, min_lat],
        [max_lng, min_lat],
        [max_lng, max_lat],
        [min_lng, max_lat],
        [min_lng, min_lat],
    ]
    return {"type": "Polygon", "coordinates": [ring]}


def build_store_document(
    session: dict,
    observations: list[dict],
    collection_id: str,
    form_id: str,
    taxon_cache: dict[str, str],
    person_token: Optional[str],
    observer_user: dict,
) -> tuple[dict, list[str]]:
    """
    One document, one gathering, N units (one per observation).
    Returns (document_dict, list of human-readable skip reasons).
    """
    skip_notes: list[str] = []

    usable_pairs: list[tuple[dict, str]] = []
    for obs in observations:
        if obs.get("has_error"):
            skip_notes.append(f"Havainto ohitettu (virhe): {obs.get('id', '')}")
            continue
        if obs.get("species_unrecognized"):
            skip_notes.append(f"Havainto ohitettu (ei lajia): {obs.get('id', '')}")
            continue
        species = (obs.get("species") or "").strip()
        if not species:
            skip_notes.append(f"Havainto ohitettu (tyhjä laji): {obs.get('id', '')}")
            continue
        lat = _parse_float(obs.get("lat"))
        lng = _parse_float(obs.get("lng"))
        if lat is None or lng is None:
            skip_notes.append(f"Havainto ohitettu (ei sijaintia): {species}")
            continue
        taxon_id = resolve_taxon_qname(species, taxon_cache, person_token=person_token)
        if not taxon_id:
            skip_notes.append(f"Lajia ei löytynyt APIsta: {species}")
            continue
        usable_pairs.append((obs, taxon_id))

    if not usable_pairs:
        raise ValueError("Ei yhtään lähetettävää havaintoa (laji/sijainti/tunnistus).")

    usable_obs = [p[0] for p in usable_pairs]
    center_lat, center_lng = _gathering_center_coords(usable_obs)
    if center_lat is None or center_lng is None:
        raise ValueError("Sijaintipuute.")

    started = session.get("startedAt") or ""

    geom = _gathering_geometry_from_observations(usable_obs)
    geom_type = geom.get("type", "?")

    leg_id = _observer_leg_identifier(observer_user)
    if not leg_id:
        raise ValueError("Havainnoijan tunnistetta ei löytynyt käyttäjäprofiilista.")

    # Havaintoerän aloitus; dateEnd jätetään tyhjäksi (ei kenttää)
    gathering_event: dict[str, Any] = {
        "dateBegin": str(started),
        "leg": [leg_id],
        "legPublic": True,
    }

    gathering: dict[str, Any] = {
        "geometry": geom,
        "units": [],
    }

    for obs, taxon_id in usable_pairs:
        lat = _parse_float(obs.get("lat"))
        lng = _parse_float(obs.get("lng"))
        assert lat is not None and lng is not None
        species = (obs.get("species") or "").strip()

        ts = obs.get("timestamp") or started
        unit: dict[str, Any] = {
            "count": str(_observation_count(obs)),
            "identifications": [
                {
                    "taxon": species
                }
            ],
            "unitFact": {
                "autocompleteSelectedTaxonID": _taxon_uri(taxon_id) 
            },
            "unitGathering": {
                "geometry": {"type": "Point", "coordinates": [lng, lat]},
                "dateBegin": str(ts),
            },
            "taxonConfidence": "MY.taxonConfidenceSure",
            "recordBasis": "MY.recordBasisHumanObservation",
        }
        note_text = _unit_notes(obs)
        if note_text:
            unit["notes"] = note_text

        gathering["units"].append(unit)

    document = {
        "collectionID": collection_id,
        "formID": form_id,
        "keywords": [
            "new",
        ],
        "secureLevel":"MX.secureLevelNone",
        "gatheringEvent": gathering_event,
        "gatherings": [gathering],
        "creator": "MA.3",
        "editor": "MA.3",
    }
    _log_info(
        "document built",
        session_id=session.get("id"),
        session_started_at=started,
        collection_id=collection_id,
        form_id=form_id,
        units=len(gathering["units"]),
        skipped=len(skip_notes),
        geometry_type=geom_type,
        observer_leg_id=leg_id,
    )
    if skip_notes:
        _log_info("skipped observations", reasons=skip_notes)
    return document, skip_notes


def submit_session_to_finbif(
    session: dict,
    observations: list[dict],
    person_token: str,
    observer_user: dict,
) -> dict[str, Any]:
    """
    POST /documents/validate first; only on success POST /documents.
    Caller must ensure session belongs to the token holder.
    """
    collection_id = FINBIF_COLLECTION_ID
    form_id = FINBIF_FORM_ID
    taxon_cache: dict[str, str] = {}

    _log_info(
        "submit start",
        session_id=session.get("id"),
        observation_rows=len(observations),
        person_id=observer_user.get("id"),
        collection_id=collection_id,
        form_id=form_id,
    )

    doc, skip_notes = build_store_document(
        session,
        observations,
        collection_id,
        form_id,
        taxon_cache,
        person_token,
        observer_user,
    )

    validate_url = "https://api.laji.fi/documents/validate?lang=fi"
    _log_info("POST documents/validate", url=validate_url)
    _log_submitted_document(doc, label="document being validated")
    try:
        v_status, v_body = common_helpers.post_finbif_json(
            validate_url, doc, person_token=person_token
        )
    except Exception as exc:
        _log("validate_request", exc)
        return {
            "ok": False,
            "error_code": "finbif_request_failed",
            "message": "FinBIF-validointipyyntö epäonnistui.",
        }

    if v_status not in (204, 201):
        _log_finbif_response("documents/validate response", v_status, v_body)
        if v_status == 422 and isinstance(v_body, dict):
            return {
                "ok": False,
                "error_code": v_body.get("errorCode", "VALIDATION_EXCEPTION"),
                "message": v_body.get("message", "Validointivirhe."),
                "details": v_body.get("details"),
                "skipped_observations": skip_notes,
            }
        msg = "Validointi epäonnistui."
        if isinstance(v_body, dict) and v_body.get("message"):
            msg = str(v_body["message"])
        return {
            "ok": False,
            "error_code": (v_body or {}).get("errorCode", "validation_failed")
            if isinstance(v_body, dict)
            else "validation_failed",
            "message": msg,
            "details": (v_body or {}).get("details") if isinstance(v_body, dict) else None,
            "skipped_observations": skip_notes,
        }

    _log_info(
        "documents/validate OK",
        http_status=v_status,
        body_empty=v_body is None,
    )

    # Validation OK — only then create (never POST /documents if validate failed above)
    create_url = "https://api.laji.fi/documents?lang=fi"
    _log_info("POST documents (create)", url=create_url)
    try:
        c_status, c_body = common_helpers.post_finbif_json(
            create_url, doc, person_token=person_token
        )
    except Exception as exc:
        _log("create_request", exc)
        return {
            "ok": False,
            "error_code": "finbif_request_failed",
            "message": "FinBIF-tallennuspyyntö epäonnistui.",
            "skipped_observations": skip_notes,
        }

    if c_status != 201:
        _log_finbif_response("documents (create) response", c_status, c_body)
        _log_submitted_document(doc)

    if c_status == 201 and isinstance(c_body, dict):
        doc_id = c_body.get("id")
        _log_info(
            "documents create OK",
            http_status=c_status,
            document_id=doc_id,
            session_id=session.get("id"),
        )
        return {
            "ok": True,
            "document": c_body,
            "document_id": doc_id,
            "skipped_observations": skip_notes,
        }

    msg = "Tallennus epäonnistui."
    if isinstance(c_body, dict) and c_body.get("message"):
        msg = str(c_body["message"])
    return {
        "ok": False,
        "error_code": (c_body or {}).get("errorCode", "create_failed")
        if isinstance(c_body, dict)
        else "create_failed",
        "message": msg,
        "details": (c_body or {}).get("details") if isinstance(c_body, dict) else None,
        "skipped_observations": skip_notes,
    }
