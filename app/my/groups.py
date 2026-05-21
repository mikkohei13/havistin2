import datetime

from helpers import common_helpers
from my.year import generate_year_dropdown

BIOTA = "MX.37600"
AGG_PAGE_SIZE = 1000
TAXA_CHUNK_SIZE = 50
PUBLIC_COUNT_TIME_FROM = 2000


def public_count_time_filter():
    """FinBIF time param for all-users column: observations from PUBLIC_COUNT_TIME_FROM onward."""
    end_year = datetime.datetime.now().year
    return f"{PUBLIC_COUNT_TIME_FROM}/{end_year}"

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


def _aggregate_url(
    page,
    aggregate_field,
    time_filter=None,
    *,
    self_as_observer=False,
    target=BIOTA,
):
    """time_filter: year int/str for one calendar year, or None for no date filter (all time)."""
    time_q = f"&time={time_filter}" if time_filter is not None else ""
    observer_q = "&selfAsObserver=true" if self_as_observer else ""
    return (
        "https://api.laji.fi/warehouse/query/unit/aggregate"
        f"?countryId=ML.206&target={target}{time_q}"
        "&individualCountMin=1"
        f"&aggregateBy={aggregate_field}"
        f"&selected={aggregate_field}"
        "&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true"
        "&cache=true&qualityIssues=NO_ISSUES&geoJSON=false&onlyCount=false"
        "&excludeNulls=true&pessimisticDateRangeHandling=false"
        f"{observer_q}"
        "&orderBy=count%20DESC"
        f"&pageSize={AGG_PAGE_SIZE}&page={page}"
    )


def fetch_aggregate_pages(
    token,
    aggregate_field,
    time_filter=None,
    *,
    self_as_observer=False,
    target=BIOTA,
):
    all_rows = []
    page = 1
    person_token = token if self_as_observer else None
    while True:
        url = _aggregate_url(
            page,
            aggregate_field,
            time_filter=time_filter,
            self_as_observer=self_as_observer,
            target=target,
        )
        data = common_helpers.fetch_finbif_api(url, person_token=person_token)
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


def fetch_public_counts_for_taxa(aggregate_field, taxon_ids, time_filter):
    """Observation counts from all observers for the given taxon ids (chunked target=)."""
    counts = {}
    for chunk in _chunks(list(taxon_ids), TAXA_CHUNK_SIZE):
        target = ",".join(chunk)
        rows = fetch_aggregate_pages(
            None,
            aggregate_field,
            time_filter=time_filter,
            self_as_observer=False,
            target=target,
        )
        counts.update(_counts_by_id(rows, aggregate_field))
    return counts


def fetch_observer_counts_for_taxa(token, aggregate_field, taxon_ids, time_filter):
    """Logged-in user's observation counts for the given taxon ids (chunked target=)."""
    counts = {}
    for chunk in _chunks(list(taxon_ids), TAXA_CHUNK_SIZE):
        target = ",".join(chunk)
        rows = fetch_aggregate_pages(
            token,
            aggregate_field,
            time_filter=time_filter,
            self_as_observer=True,
            target=target,
        )
        counts.update(_counts_by_id(rows, aggregate_field))
    return counts


def fetch_full_public_counts(aggregate_field, time_filter):
    """All taxon groups at this rank with observations in Finland (paginated BIOTA query)."""
    rows = fetch_aggregate_pages(
        None,
        aggregate_field,
        time_filter=time_filter,
        self_as_observer=False,
        target=BIOTA,
    )
    return _counts_by_id(rows, aggregate_field)


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
    html["document_title"] = f"{DOCUMENT_TITLE_PREFIX[rank]} {year}"

    html["year_options"] = generate_year_dropdown(1970)
    end_year = datetime.datetime.now().year
    html["public_time_laji"] = (
        f"{PUBLIC_COUNT_TIME_FROM}-01-01/{end_year}-12-31"
    )

    html["needs_login"] = not token
    html["api_error"] = False
    html["got_results"] = False
    html["rank_taxa"] = []
    html["mx_qnames_not_in_year"] = []

    if not token:
        return html

    agg_field = RANK_AGGREGATE_FIELD[rank]

    public_time = public_count_time_filter()

    try:
        count_public = fetch_full_public_counts(agg_field, public_time)
        id_set = set(count_public)
        if not id_set:
            return html

        user_all_counts = _counts_by_id(
            fetch_aggregate_pages(
                token, agg_field, time_filter=None, self_as_observer=True
            ),
            agg_field,
        )
        user_year_counts = _counts_by_id(
            fetch_aggregate_pages(
                token, agg_field, time_filter=year, self_as_observer=True
            ),
            agg_field,
        )
    except Exception as e:
        print(f"my.groups: aggregate failed: {e}", flush=True)
        html["api_error"] = True
        return html

    try:
        name_map = resolve_taxon_names(id_set)
    except Exception as e:
        print(f"my.groups: taxa lookup failed: {e}", flush=True)
        name_map = {}

    merged = []
    for tid in id_set:
        nm = name_map.get(tid, {})
        cy = user_year_counts.get(tid, 0)
        ca = user_all_counts.get(tid, 0)
        merged.append(
            {
                "id": tid,
                "count": cy,
                "count_all": ca,
                "count_public": count_public.get(tid, 0),
                "fi": nm.get("fi") or "",
                "sci": nm.get("sci") or "",
                "taxonomic_order": nm.get("taxonomic_order"),
            }
        )

    merged.sort(
        key=lambda x: (
            -x["count_public"],
            -x["count"],
            x["taxonomic_order"] is None,
            x["taxonomic_order"] if x["taxonomic_order"] is not None else 0,
            x["fi"] or x["sci"] or x["id"],
        )
    )

    not_in_year = [r for r in merged if r["count"] == 0 and r["count_all"] > 0]
    not_in_year.sort(
        key=lambda x: (
            x["taxonomic_order"] is None,
            x["taxonomic_order"] if x["taxonomic_order"] is not None else 0,
            x["fi"] or x["sci"] or x["id"],
        )
    )
    html["mx_qnames_not_in_year"] = [r["id"] for r in not_in_year]

    html["rank_taxa"] = merged

    # Count taxa (must match visible table rows)
    html["taxacount_own_year"] = 0
    html["taxacount_own_all"] = 0
    html["taxacount_public"] = 0

    for taxonrow in merged:
        if taxonrow["count"] > 0:
            html["taxacount_own_year"] = html["taxacount_own_year"] + 1
        if taxonrow["count_all"] > 0:
            html["taxacount_own_all"] = html["taxacount_own_all"] + 1
        if taxonrow["count_public"] > 0:
            html["taxacount_public"] = html["taxacount_public"] + 1

    html["got_results"] = True

    return html

