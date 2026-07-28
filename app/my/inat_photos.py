import time
from urllib.parse import quote

from helpers import common_helpers
import taxa.cache_db as cache_db


DISALLOWED = {None, "ARR", ""}


def _connect():
    return cache_db.connect_inat_photo_db()


def author_from_attribution(attribution):
    if not attribution:
        return ""
    return attribution.split(",")[0].replace("(c) ", "").replace("(c)", "").strip()


def _fetch_from_inat(scientific_name):
    data = common_helpers.fetch_api(
        f"https://api.inaturalist.org/v1/search?q={quote(scientific_name)}"
        f"&locale=fi&preferred_place_id=7020&per_page=5",
        False,
    )
    if not data.get("total_results"):
        return None

    record = data["results"][0].get("record") or {}

    # If name cannot be exactly matched, don't return images
    if record["name"] != scientific_name:
        return None

    for photo in record.get("taxon_photos") or []:
        p = photo.get("photo") or {}
        license_code = p.get("license_code")
        if license_code in DISALLOWED:
            continue
        attribution = p.get("attribution", "")
        return {
            "image_url": p.get("medium_url") or p.get("small_url") or p.get("square_url"),
            "attribution": attribution,
            "author": author_from_attribution(attribution),
            "license_code": license_code,
            "license_html": common_helpers.cc_abbreviation(license_code),
            "source_url": p.get("native_page_url", ""),
            "fetched_at": int(time.time()),
        }
    return None


def get_photo(qname, scientific_name):
    coll = _connect()
    cached = coll.find_one({"_id": qname})
    if cached:
        if not cached.get("author") and cached.get("attribution"):
            cached["author"] = author_from_attribution(cached["attribution"])
        return cached

    photo = _fetch_from_inat(scientific_name)
    if not photo:
        photo = {
            "image_url": None,
            "attribution": "",
            "author": "",
            "license_code": None,
            "license_html": "",
            "source_url": "",
            "fetched_at": int(time.time()),
        }

    coll.update_one({"_id": qname}, {"$set": photo}, upsert=True)
    photo["_id"] = qname
    return photo
