"""Best-effort append-only logging of Havis transcriptions to MongoDB (demo analytics).

Optional in production: index ``{"at": -1}`` on ``havistin.havis_transcription_logs`` for time-range queries.
"""

import sys
from datetime import datetime

from pymongo import MongoClient

import app_secrets

_DB = "havistin"
_COLLECTION = "havis_transcription_logs"


def log_transcription(at: datetime, transcript: str, structured: dict) -> None:
    if not (app_secrets.mongodb_user and app_secrets.mongodb_pass and app_secrets.mongodb_server):
        return
    uri = "mongodb+srv://%s:%s@%s/?retryWrites=true&w=majority" % (
        app_secrets.mongodb_user,
        app_secrets.mongodb_pass,
        app_secrets.mongodb_server,
    )
    client = None
    try:
        client = MongoClient(uri)
        coll = client[_DB][_COLLECTION]
        coll.insert_one(
            {
                "at": at,
                "transcript": transcript,
                "structured": structured,
            }
        )
    except Exception as exc:
        print(
            f"Havis transcription log: insert failed ({type(exc).__name__}): {exc}",
            file=sys.stdout,
        )
    finally:
        if client is not None:
            client.close()
