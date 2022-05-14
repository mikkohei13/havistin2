
import atlas.common as common

def breeding_html(atlas_class):

    if "MY.atlasClassEnumD" == atlas_class:
        heading = "Varmat pesinnät"
    elif "MY.atlasClassEnumC" == atlas_class:
        heading = "Todennäköiset pesinnät"
    # TODO: exception for other cases

    data = common.fetch_finbif_api("https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=unit.linkings.originalTaxon.speciesNameFinnish&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=30&page=1&cache=true&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&yearMonth=2022%2F2025&individualCountMin=1&qualityIssues=NO_ISSUES&time=-14%2F0&atlasClass=" + atlas_class + "&access_token=")

    html = f"<h3>{heading} (top 20)</h3>"
    html += "<p>Näistä lajeista on tehty eniten havaintoja viimeisen kahden viikon aikana, eli niitä kannattaa erityisesti tarkkailla. Arkaluontoiset havainnot eivät ole tässä taulukossa mukana.</p>"
    html += "<table class='styled-table'>"
    html += "<thead><tr><th>Laji</th><th>Havaintoja</th></tr></thead>"
    html += "<tbody>"

    for item in data["results"]:
        aggregate_by = item["aggregateBy"]["unit.linkings.originalTaxon.speciesNameFinnish"]
        count = str(item["count"])
        html += "<tr><td>" + aggregate_by + "</td>"
        html += "<td>" + count + "</td>"

    html += "</tbody></table>"
    return html


def main():
    html = dict()

#    breeding_data_dict = breeding_data("D")
    html["breeding_certain"] = breeding_html("MY.atlasClassEnumD")

#    breeding_data_dict = breeding_data("C")
    html["breeding_probable"] = breeding_html("MY.atlasClassEnumC")

    return html
