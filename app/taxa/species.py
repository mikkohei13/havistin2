
import taxa.common as common


def main(taxon_id_untrusted):

    valid_qname = common.valid_qname(taxon_id_untrusted)
    
    html = dict()

    # &selectedFields=id,vernacularName,scientificName,typeOfOccurrenceInFinland,parent.family.scientificName,observationCountFinland
    species_data = common.fetch_finbif_api(f"https://api.laji.fi/v0/taxa/{valid_qname}/species?onlyFinnish=true&lang=fi&page=1&pageSize=10&sortOrder=taxonomic&access_token=")

    # Expecting only one species
    html["raw_data"] = species_data["results"][0]

    common.print_log(species_data)

    html["occurrence_status"] = common.fetch_variable_label(html["raw_data"]["typeOfOccurrenceInFinland"][0])

    html["primary_habitat"] = common.fetch_variable_label(html["raw_data"]["primaryHabitat"]["habitat"])

    html["redlist_status"] = common.fetch_variable_label(html["raw_data"]["latestRedListStatusFinland"]["status"])
    html["redlist_year"] = html["raw_data"]["latestRedListStatusFinland"]["year"]

    '''
    <p>Esiintymisen tyyppi: typeOfOccurrenceInFinland</p>

    <p>Ensisijainen habitaatti: primaryHabitat:habitat</p>

    <p>Id: qname</p>

    <p>Uhanalaisuusluokka: latestRedListStatusFinland:status / year</p>
    '''


#    html["scientific_name"] = species_data["scientificName"]
#    html["obs_count_finland"] = species_data["observationCountFinland"]


    return html
