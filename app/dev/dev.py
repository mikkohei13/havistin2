
import atlas.common_atlas as common_atlas
from helpers import common_helpers

def species_list(date_filter):
    date_filter = date_filter.replace("/", "%2F")

#    https://api.laji.fi/v0/warehouse/query/unit/aggregate?onlyCount=true&taxonCounts=false&gatheringCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=100&page=1&cache=false&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&time=-7%2F0&collectionIdNot=HR.48%2CHR.3671%2CHR.2029&individualCountMin=1&qualityIssues=NO_ISSUES&access_token=

    url = f"https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=unit.linkings.originalTaxon.speciesNameFinnish&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=1000&page=1&cache=true&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&yearMonth=2022%2F2025&individualCountMin=1&qualityIssues=NO_ISSUES&reliability=RELIABLE,UNDEFINED&time={ date_filter }&collectionIdNot=HR.48%2CHR.3671%2CHR.2029&access_token="
    data = common_helpers.fetch_finbif_api(url)
#    print(data)

    species_counts = dict()
    for item in data["results"]:
        species = item["aggregateBy"]["unit.linkings.originalTaxon.speciesNameFinnish"]
        count = item["count"]
        species_counts[species] = count;

    print(species_counts)
    return species_counts


def make_change_html(species_this_year, species_last_year):
    
    html = "<table>\n"
    html += "<tr>"
    html += "<th>Laji</th>"
    html += "<th>Viime viikko</th>"
    html += "<th>Viime vuonna</th>"
    html += "<th>Suhde</th>"
    html += "</tr>\n"

    for species, count in species_this_year.items():
        if species in species_last_year:
            count_last_year = species_last_year[species]
            proportion = str(round(count / count_last_year, 2))
        else:
            proportion = "+"
            count_last_year = 0

        html += "<tr>"
        html += f"<td>{ species }</td>"
        html += f"<td>{ count }</td>"
        html += f"<td>{ count_last_year }</td>"
        html += f"<td>{ proportion }</td>"
        html += "</tr>\n"
        
    html += "</table>"

    return html



def main(param):
    html = dict()

    species_this_year = species_list("-7/0")
    species_last_year = species_list("-372/-365")

    html["data"] = make_change_html(species_this_year, species_last_year)

    return html
