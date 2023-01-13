
import taxa.common_taxa as common_taxa
from helpers import common_helpers

def generate_list(data):

    family_mem = ""
    html = ""

    for item in data["results"]:
#        common_helpers.print_log(item)
#        exit()

        family = item["parent"]["family"]["scientificName"]
        if family != family_mem:
            html += "</ul>"
            html += "<h4>" + family + "</h4>"
            html += "<ul class='taxonlist'>"
            family_mem = family

        if "vernacularName" in item:
            vernacular_name = item['vernacularName']
        else:
            vernacular_name = "ei suomenkielistä nimeä"

        if "typeOfOccurrenceInFinland" in item:
            type_of_occurrence_finland = item['typeOfOccurrenceInFinland'][0]
        else:
            type_of_occurrence_finland = "ei esiintymistietoa"

        html += "<li>"
        html += f"<a href='/taxa/species/{item['id']}'>"
        html += f"<em>{item['scientificName']}</em> - {vernacular_name}"
        html += "</a>"
        html += f" ({item['observationCountFinland']}) {type_of_occurrence_finland}"
        html += "</li>"

    html += "</ul>"
    return html

def main(taxon_id_untrusted):

    valid_qname = common_taxa.valid_qname(taxon_id_untrusted)
    
    html = dict()

    taxon_data = common_helpers.fetch_finbif_api(f"https://api.laji.fi/v0/taxa/{valid_qname}?lang=fi&langFallback=true&maxLevel=0&includeHidden=false&includeMedia=false&includeDescriptions=false&includeRedListEvaluations=false&sortOrder=taxonomic&access_token=")

    html["vernacular_name"] = taxon_data["vernacularName"]
    html["finnish_species_count"] = taxon_data["countOfFinnishSpecies"]
    html["scientific_name"] = taxon_data["scientificName"]
    html["obs_count_finland"] = taxon_data["observationCountFinland"]

    max_species = 1000
    species_data = common_helpers.fetch_finbif_api(f"https://api.laji.fi/v0/taxa/{valid_qname}/species?onlyFinnish=true&selectedFields=id,vernacularName,scientificName,typeOfOccurrenceInFinland,parent.family.scientificName,observationCountFinland&lang=fi&page=1&pageSize={max_species}&sortOrder=taxonomic&access_token=")

    html["list"] = generate_list(species_data)

# https://api.laji.fi/v0/taxa/MX.229577/species?onlyFinnish=true&selectedFields=id,vernacularName,scientificName,typeOfOccurrenceInFinland,primaryHabitat,secondaryHabitats,latestRedListStatusFinland&lang=fi&page=1&pageSize=1000&sortOrder=taxonomic&access_token=8N7b0asX4eKbbv8VaLOFLRI9wev5iGYuTekXBmsohSRKy5bvcfqHFYBGo1ohymSm

    return html
