
import atlas.common_atlas as common_atlas
from helpers import common_helpers

def breeding_html(probablility):

    if "certain" == probablility:
        filters = "atlasClass=MY.atlasClassEnumD"
    elif "probable_6" == probablility:
        heading = "Todennäköiset pesinnät, vain indeksi 6-66"
        filters = "atlasCode=MY.atlasCodeEnum6%2CMY.atlasCodeEnum61%2CMY.atlasCodeEnum62%2CMY.atlasCodeEnum63%2CMY.atlasCodeEnum64%2CMY.atlasCodeEnum65%2CMY.atlasCodeEnum66"
    elif "probable" == probablility:
        filters = "atlasClass=MY.atlasClassEnumC"
    # TODO: exception for other cases

    data = common_helpers.fetch_finbif_api("https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=unit.linkings.originalTaxon.speciesNameFinnish&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=30&page=1&cache=true&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&yearMonth=2022%2F2025&individualCountMin=1&qualityIssues=NO_ISSUES&reliability=RELIABLE,UNDEFINED&time=-14%2F0&" + filters + "&access_token=")

    html = ""
    html += "<table class='styled-table'>"
    html += "<thead><tr><th>Laji</th><th>Havaintoja</th></tr></thead>"
    html += "<tbody>"

    for item in data["results"]:
        species = item["aggregateBy"]["unit.linkings.originalTaxon.speciesNameFinnish"]
        count = str(item["count"])
        html += "<tr><td><a href='/atlas/laji/" + species + "'>" + species + "</a></td>"
        html += "<td>" + count + "</td>"

    html += "</tbody></table>"
    return html


def main():
    html = dict()

    html["breeding_certain"] = breeding_html("certain")

    html["breeding_probable_6"] = breeding_html("probable_6")

    html["breeding_probable"] = breeding_html("probable")

    return html
