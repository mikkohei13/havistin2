import io
import sys
import traceback

from flask import Blueprint, jsonify, redirect, render_template, request, session
from openai import OpenAI

import app_secrets

from app.havis_finbif_submit import submit_session_to_finbif
from app.havis_structurization import GPT_MODEL, structurize_transcript

havis_bp = Blueprint("havis", __name__, url_prefix="/havis")

TRANSCRIBE_MODEL = "gpt-4o-transcribe"

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
        result = structurize_transcript(raw_transcript, client=client)
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

    return jsonify(result)


@havis_bp.route("/api/submit", methods=["POST"])
def havis_submit():
    user_data = session.get("user_data")
    if user_data is None or "errorCode" in user_data:
        return _unauthorized()

    person_token = session.get("token")
    if not person_token:
        return jsonify(
            {"ok": False, "error_code": "unauthorized", "message": "Kirjautuminen puuttuu."}
        ), 401

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"ok": False, "error_code": "bad_request", "message": "Virheellinen JSON."}), 400

    sess = payload.get("session")
    observations = payload.get("observations")
    if not isinstance(sess, dict) or not isinstance(observations, list):
        return jsonify({"ok": False, "error_code": "bad_request", "message": "Puuttuva session tai observations."}), 400

    expected_uid = user_data.get("id")
    if expected_uid is not None:
        expected_uid = str(expected_uid)
    session_uid = sess.get("userId")
    if session_uid is not None:
        session_uid = str(session_uid)
    if expected_uid and session_uid and session_uid != expected_uid:
        return jsonify({"ok": False, "error_code": "forbidden", "message": "Väärä käyttäjä."}), 403

    ended = sess.get("endedAt")
    if not ended or str(ended).strip() == "":
        return jsonify(
            {"ok": False, "error_code": "bad_request", "message": "Havaintoerä ei ole päättynyt."}
        ), 400

    print(
        f"Havis API /api/submit: session_id={sess.get('id')} "
        f"observations={len(observations)} user_id={user_data.get('id')}",
        file=sys.stdout,
    )

    try:
        result = submit_session_to_finbif(sess, observations, person_token, user_data)
    except ValueError as err:
        return jsonify({"ok": False, "error_code": "bad_request", "message": str(err)}), 400
    except Exception as err:
        _log_havis_error("finbif_submit", err)
        return jsonify(
            {"ok": False, "error_code": "server_error", "message": "FinBIF-lähetys epäonnistui."}
        ), 502

    print(
        f"Havis API /api/submit response: ok={result.get('ok')} "
        f"error_code={result.get('error_code')} document_id={result.get('document_id')}",
        file=sys.stdout,
    )

    status = 200 if result.get("ok") else 400
    return jsonify(result), status
