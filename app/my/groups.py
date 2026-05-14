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


def _aggregate_url(page, aggregate_field, time_filter=None):
    """time_filter: year int/str for one calendar year, or None for no date filter (all time)."""
    time_q = f"&time={time_filter}" if time_filter is not None else ""
    return (
        "https://api.laji.fi/warehouse/query/unit/aggregate"
        f"?countryId=ML.206&target={BIOTA}{time_q}"
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


def fetch_aggregate_pages(token, aggregate_field, time_filter=None):
    all_rows = []
    page = 1
    while True:
        url = _aggregate_url(page, aggregate_field, time_filter=time_filter)
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


def _counts_by_id(rows, aggregate_field):
    return {item["id"]: item["count"] for item in _parse_aggregate_rows(rows, aggregate_field)}


def _chunks(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def _parse_taxonomic_order(raw):
    if raw is None:
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def resolve_taxon_names(qnames):
    """Map MX qname -> {fi, sci, taxonomic_order} using batched GET /taxa (no person token)."""
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
            names[qn] = {
                "fi": fi,
                "sci": sci,
                "taxonomic_order": _parse_taxonomic_order(item.get("taxonomicOrder")),
            }
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
        rows_year = fetch_aggregate_pages(token, agg_field, time_filter=year)
        rows_all = fetch_aggregate_pages(token, agg_field, time_filter=None)
    except Exception as e:
        print(f"my.groups: aggregate failed: {e}", flush=True)
        html["api_error"] = True
        return html

    count_year = _counts_by_id(rows_year, agg_field)
    count_all = _counts_by_id(rows_all, agg_field)
    id_set = set(count_year) | set(count_all)
    if not id_set:
        return html

    try:
        name_map = resolve_taxon_names(id_set)
    except Exception as e:
        print(f"my.groups: taxa lookup failed: {e}", flush=True)
        name_map = {}

    merged = []
    for tid in id_set:
        nm = name_map.get(tid, {})
        cy = count_year.get(tid, 0)
        ca = count_all.get(tid, 0)
        merged.append(
            {
                "id": tid,
                "count": cy,
                "count_all": ca,
                "fi": nm.get("fi") or "",
                "sci": nm.get("sci") or "",
                "taxonomic_order": nm.get("taxonomic_order"),
            }
        )

    merged.sort(
        key=lambda x: (
            -x["count"],
            -x["count_all"],
            x["taxonomic_order"] is None,
            x["taxonomic_order"] if x["taxonomic_order"] is not None else 0,
            x["fi"] or x["sci"] or x["id"],
        )
    )

    html["families"] = merged
    html["got_results"] = True

    return html
