import datetime

from helpers import common_helpers
from my.year import generate_year_dropdown

BIOTA = "MX.37600"
AGG_PAGE_SIZE = 1000
TAXA_CHUNK_SIZE = 50


def _family_qname(family_id_raw):
    if not family_id_raw:
        return None
    return str(family_id_raw).replace("http://tun.fi/", "").strip()


def _family_aggregate_url(year, page):
    return (
        "https://api.laji.fi/warehouse/query/unit/aggregate"
        f"?countryId=ML.206&target={BIOTA}&time={year}"
        "&individualCountMin=1"
        "&aggregateBy=unit.linkings.taxon.familyId"
        "&selected=unit.linkings.taxon.familyId"
        "&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true"
        "&cache=true&qualityIssues=NO_ISSUES&geoJSON=false&onlyCount=false"
        "&excludeNulls=true&pessimisticDateRangeHandling=false"
#        "&taxonCounts=false&gatheringCounts=false&pairCounts=false&atlasCounts=false"
        "&selfAsObserver=true"
        "&orderBy=count%20DESC"
        f"&pageSize={AGG_PAGE_SIZE}&page={page}"
    )



def fetch_family_aggregate_pages(token, year):
    all_rows = []
    page = 1
    while True:
        url = _family_aggregate_url(year, page)
        data = common_helpers.fetch_finbif_api(url, person_token=token)
        rows = data.get("results") or []
        if not rows:
            break
        all_rows.extend(rows)
        if len(rows) < AGG_PAGE_SIZE:
            break
        current = data.get("currentPage", page)
        last = data.get("lastPage", current)
        if current >= last:
            break
        page += 1

    return all_rows


def _parse_aggregate_rows(rows):
    """Build list of {id, count} from warehouse aggregate results."""
    out = []
    for row in rows:
        agg = row.get("aggregateBy") or {}
        raw_id = agg.get("unit.linkings.taxon.familyId")
        qname = _family_qname(raw_id)
        if not qname:
            continue
        try:
            cnt = int(row.get("count", 0))
        except (TypeError, ValueError):
            cnt = 0
        out.append({"id": qname, "count": cnt})
    return out


def _chunks(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def resolve_taxon_names(qnames):
    """Map MX qname -> {fi, sci} using batched GET /taxa (no person token)."""
    names = {}
    for chunk in _chunks(list(qnames), TAXA_CHUNK_SIZE):
        id_param = ",".join(chunk)
        url = (
            "https://api.laji.fi/taxa"
            f"?id={id_param}&lang=fi&langFallback=true&page=1&pageSize={len(chunk)}"
            "&checklistVersion=current&includeHidden=false&includeMedia=false"
            "&includeDescriptions=false&includeRedListEvaluations=false&sortOrder=taxonomic"
        )
        data = common_helpers.fetch_finbif_api(url)
        for item in data.get("results") or []:
            tid = item.get("id") or ""
            qn = _family_qname(tid)
            if not qn:
                continue
            fi = item.get("vernacularName") or ""
            sci = item.get("scientificName") or ""
            names[qn] = {"fi": fi, "sci": sci}
    return names


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

    html["needs_login"] = not token
    html["api_error"] = False
    html["got_results"] = False
    html["families"] = []

    if not token:
        return html

    try:
        rows = fetch_family_aggregate_pages(token, year)
    except Exception as e:
        print(f"my.groups: aggregate failed: {e}", flush=True)
        html["api_error"] = True
        return html

    families_raw = _parse_aggregate_rows(rows)
    if not families_raw:
        return html

    id_set = {f["id"] for f in families_raw}
    try:
        name_map = resolve_taxon_names(id_set)
    except Exception as e:
        print(f"my.groups: taxa lookup failed: {e}", flush=True)
        name_map = {}

    merged = []
    for f in families_raw:
        nm = name_map.get(f["id"], {})
        merged.append(
            {
                "id": f["id"],
                "count": f["count"],
                "fi": nm.get("fi") or "",
                "sci": nm.get("sci") or "",
            }
        )

    merged.sort(key=lambda x: (-x["count"], x["fi"] or x["sci"] or x["id"]))

    html["families"] = merged
    html["got_results"] = True

    return html
