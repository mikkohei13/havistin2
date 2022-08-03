
import taxa.common as common

def generate_list(data):

    family_mem = ""
    html = ""

    for item in data["results"]:
        family = item["parent"]["family"]["scientificName"]
        if family != family_mem:
            html += "</ul>"
            html += "<h4>" + family + "</h4>"
            html += "<ul>"
            family_mem = family

        html += "<li>"
        html += f"<a href='/taxa/species/{item['id']}'>"
        html += item["scientificName"] + " - " + item["vernacularName"]
        html += "</a>"
        html += f" ({item['observationCountFinland']}) {item['typeOfOccurrenceInFinland'][0]}"
        html += "</li>"

        common.print_log(item["vernacularName"])

    html += "</ul>"
    return html

def main(taxon_id_untrusted):

    valid_qname = common.valid_qname(taxon_id_untrusted)
    
    html = dict()

    taxon_data = common.fetch_finbif_api(f"https://api.laji.fi/v0/taxa/{valid_qname}?lang=fi&langFallback=true&maxLevel=0&includeHidden=false&includeMedia=false&includeDescriptions=false&includeRedListEvaluations=false&sortOrder=taxonomic&access_token=")

    html["vernacular_name"] = taxon_data["vernacularName"]
    html["finnish_species_count"] = taxon_data["countOfFinnishSpecies"]
    html["scientific_name"] = taxon_data["scientificName"]
    html["obs_count_finland"] = taxon_data["observationCountFinland"]

    max_species = 20
    species_data = common.fetch_finbif_api(f"https://api.laji.fi/v0/taxa/{valid_qname}/species?onlyFinnish=true&selectedFields=id,vernacularName,scientificName,typeOfOccurrenceInFinland,parent.family.scientificName,observationCountFinland&lang=fi&page=1&pageSize={max_species}&sortOrder=taxonomic&access_token=")

#    common.print_log(taxon_data)

    html["list"] = generate_list(species_data)

# https://api.laji.fi/v0/taxa/MX.229577/species?onlyFinnish=true&selectedFields=id,vernacularName,scientificName,typeOfOccurrenceInFinland,primaryHabitat,secondaryHabitats,latestRedListStatusFinland&lang=fi&page=1&pageSize=1000&sortOrder=taxonomic&access_token=8N7b0asX4eKbbv8VaLOFLRI9wev5iGYuTekXBmsohSRKy5bvcfqHFYBGo1ohymSm

    return html
