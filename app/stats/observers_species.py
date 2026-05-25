import datetime
import html
from urllib.parse import urlencode

from helpers import common_helpers
from helpers.year_dropdown import generate_year_dropdown

_API_BASE = "https://api.laji.fi/warehouse/query/unit/aggregate"




def _fetch_aggregate(year=None):
    params = {
        "aggregateBy": "gathering.team.memberName",
        "orderBy": "speciesCount DESC",
        "onlyCount": "true",
        "taxonCounts": "true",
        "gatheringCounts": "false",
        "pairCounts": "false",
        "atlasCounts": "false",
        "excludeNulls": "true",
        "pessimisticDateRangeHandling": "false",
        "pageSize": "100",
        "page": "1",
        "cache": "false",
        "useIdentificationAnnotations": "true",
        "includeSubTaxa": "true",
        "includeNonValidTaxa": "true",
        "individualCountMin": "1",
        "includeNullLoadDates": "false",
        "qualityIssues": "NO_ISSUES",
        "countryId": "ML.206",
        "wild": "WILD,WILD_UNKNOWN",
        "higherTaxon": "false",
        "lang": "fi",
    }
    if year is not None:
        params["time"] = str(year)
    url = f"{_API_BASE}?{urlencode(params)}"
    return common_helpers.fetch_finbif_api(url)

def main(year_untrusted=None):
    current_year = datetime.datetime.now().year
    if year_untrusted is not None:
        year = int(year_untrusted)
        if year < 1970:
            year = current_year
        elif year > current_year:
            year = current_year
    else:
        year = None

    data = _fetch_aggregate(year=year)
    total = data.get("total", 0)
    results = list(data.get("results", []))

    taxon_counts = [
        r["taxonCount"]
        for r in results
        if isinstance(r.get("taxonCount"), (int, float))
    ]
    if taxon_counts:
        min_taxon = min(taxon_counts)
        filtered = [r for r in results if r.get("speciesCount", 0) >= min_taxon]
    else:
        min_taxon = None
        filtered = results

    rows = []
    for item in filtered:
        name = item.get("aggregateBy", {}).get("gathering.team.memberName", "")
        species = item.get("speciesCount", 0)
        rows.append(
            "<tr><td>"
            + html.escape(str(name), quote=True)
            + "</td><td>"
            + html.escape(str(species), quote=True)
            + "</td></tr>"
        )

    table = (
        "<table class='styled-table'>"
        "<thead><tr><th>Havainnoija</th><th>Lajeja</th></tr></thead>"
        "<tbody>"
        + "".join(rows)
        + "</tbody></table>"
    )

    return {
        "table": table,
        "total": total,
        "page_size": len(rows),
        "min_taxon": min_taxon,
        "year": year,
        "year_options": generate_year_dropdown(1970),
    }
