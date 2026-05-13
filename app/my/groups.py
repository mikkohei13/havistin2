import datetime

from helpers import common_helpers
from my.year import generate_year_dropdown

BIOTA = "MX.37600"
AGG_PAGE_SIZE = 1000
TAXA_CHUNK_SIZE = 50

VALID_RANKS = frozenset({"phylum", "class", "order", "family"})

# Warehouse aggregateBy / selected field (unit.linkings.taxon.*)
RANK_AGGREGATE_FIELD = {
    "phylum": "unit.linkings.taxon.phylumId",
    "class": "unit.linkings.taxon.classId",
    "order": "unit.linkings.taxon.orderId",
    "family": "unit.linkings.taxon.familyId",
}

RANK_H1 = {
    "phylum": "Pääjaksoittain Suomesta",
    "class": "Omat luokat Suomesta",
    "order": "Omat lahkot Suomesta",
    "family": "Omat heimot Suomesta",
}

RANK_COUNT_LABEL = {
    "phylum": "Pääjaksoja",
    "class": "Luokkia",
    "order": "Lahkoja",
    "family": "Heimoja",
}

DOCUMENT_TITLE_PREFIX = {
    "phylum": "Havainnot pääjaksoittain",
    "class": "Omat luokat",
    "order": "Omat lahkot",
    "family": "Omat heimot",
}


def _taxon_qname(raw):
    if not raw:
        return None
    return str(raw).replace("http://tun.fi/", "").strip()


def _normalize_rank(rank_untrusted):
    if not rank_untrusted:
        return "family"
    r = str(rank_untrusted).strip().lower()
    return r if r in VALID_RANKS else "family"


def _aggregate_url(year, page, aggregate_field):
    return (
        "https://api.laji.fi/warehouse/query/unit/aggregate"
        f"?countryId=ML.206&target={BIOTA}&time={year}"
        "&individualCountMin=1"
        f"&aggregateBy={aggregate_field}"
        f"&selected={aggregate_field}"
        "&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true"
        "&cache=true&qualityIssues=NO_ISSUES&geoJSON=false&onlyCount=false"
        "&excludeNulls=true&pessimisticDateRangeHandling=false"
        "&selfAsObserver=true"
        "&orderBy=count%20DESC"
        f"&pageSize={AGG_PAGE_SIZE}&page={page}"
    )


def fetch_aggregate_pages(token, year, aggregate_field):
    all_rows = []
    page = 1
    while True:
        url = _aggregate_url(year, page, aggregate_field)
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


def _parse_aggregate_rows(rows, aggregate_field):
    """Build list of {id, count} from warehouse aggregate results."""
    out = []
    for row in rows:
        agg = row.get("aggregateBy") or {}
        raw_id = agg.get(aggregate_field)
        qname = _taxon_qname(raw_id)
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
            qn = _taxon_qname(tid)
            if not qn:
                continue
            fi = item.get("vernacularName") or ""
            sci = item.get("scientificName") or ""
            names[qn] = {"fi": fi, "sci": sci}
    return names


def main(token, year_untrusted, rank_untrusted):
    html = dict()

    current_year = datetime.datetime.now().year
    if year_untrusted < 1900:
        year = current_year
    elif year_untrusted > current_year:
        year = current_year
    else:
        year = year_untrusted
    html["year"] = year

    rank = _normalize_rank(rank_untrusted)
    html["rank"] = rank
    html["rank_h1"] = RANK_H1[rank]
    html["rank_count_label"] = RANK_COUNT_LABEL[rank]
    html["document_title"] = f"{DOCUMENT_TITLE_PREFIX[rank]} {year}"

    html["year_options"] = generate_year_dropdown(1970)

    html["needs_login"] = not token
    html["api_error"] = False
    html["got_results"] = False
    html["families"] = []

    if not token:
        return html

    agg_field = RANK_AGGREGATE_FIELD[rank]

    try:
        rows = fetch_aggregate_pages(token, year, agg_field)
    except Exception as e:
        print(f"my.groups: aggregate failed: {e}", flush=True)
        html["api_error"] = True
        return html

    rows_parsed = _parse_aggregate_rows(rows, agg_field)
    if not rows_parsed:
        return html

    id_set = {f["id"] for f in rows_parsed}
    try:
        name_map = resolve_taxon_names(id_set)
    except Exception as e:
        print(f"my.groups: taxa lookup failed: {e}", flush=True)
        name_map = {}

    merged = []
    for f in rows_parsed:
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
