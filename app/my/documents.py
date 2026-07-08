import datetime
from urllib.parse import urlencode

from helpers import common_helpers
from helpers.year_dropdown import generate_year_dropdown

SELECTED_FIELDS = (
    "creator,id,gatherings[*].id,publicityRestrictions,formID,dateEdited,"
    "gatheringEvent.dateEnd,gatheringEvent.dateBegin,gatherings.dateBegin,"
    "gatherings.dateEnd,gatherings.locality,namedPlaceID,gatherings.namedPlaceID,"
    "gatherings.municipality,gatherings.units,gatheringEvent.leg"
)



def get_documents(token, year):
    params = {
        "selectedFields": SELECTED_FIELDS,
        "observationYear": year,
        "page": 1,
        "pageSize": 10000,
    }
    url = f"https://api.laji.fi/documents?{urlencode(params)}"
    return common_helpers.fetch_finbif_api(url, person_token=token)


def _parse_date_begin(date_begin):
    if not date_begin:
        return None
    try:
        normalized = date_begin.replace("Z", "+00:00")
        if len(normalized) == 16:
            return datetime.datetime.fromisoformat(normalized)
        return datetime.datetime.fromisoformat(normalized[:19])
    except ValueError:
        return None


def _format_date_begin(dt):
    if not dt:
        return "—"
    if dt.hour or dt.minute:
        return f"{dt.day}.{dt.month}.{dt.year} {dt.hour}:{dt.minute:02d}"
    return f"{dt.day}.{dt.month}.{dt.year}"


def _locality(doc):
    for gathering in doc.get("gatherings", []):
        locality = gathering.get("locality") or gathering.get("municipality")
        if locality:
            return locality
    return ""


def _unit_count(doc):
    count = 0
    for gathering in doc.get("gatherings", []):
        count += len(gathering.get("units", []))
    return count


def _document_rows(documents):
    rows = []
    for doc in documents:
        date_begin_raw = doc.get("gatheringEvent", {}).get("dateBegin")
        date_begin_dt = _parse_date_begin(date_begin_raw)
        rows.append({
            "id": doc.get("id", ""),
            "form_id": doc.get("formID", ""),
            "date_begin": date_begin_dt,
            "date_display": _format_date_begin(date_begin_dt) if date_begin_dt else (date_begin_raw or "—"),
            "locality": _locality(doc),
            "unit_count": _unit_count(doc),
        })
    rows.sort(key=lambda row: row["date_begin"] or datetime.datetime.min, reverse=True)
    return rows


def main(token, year_untrusted):
    html = dict()

    current_year = datetime.datetime.now().year
    if year_untrusted < 1900:
        year = current_year
    elif year_untrusted > current_year:
        year = current_year
    else:
        year = year_untrusted
    html["year"] = year
    html["year_options"] = generate_year_dropdown(1970)
    html["logged_in"] = bool(token)

    if not token:
        html["got_results"] = False
        html["documents"] = []
        html["document_count"] = 0
        return html

    data = get_documents(token, year)
    html["documents"] = _document_rows(data.get("results", []))
    html["document_count"] = data.get("total", len(html["documents"]))
    html["got_results"] = len(html["documents"]) > 0

    return html
