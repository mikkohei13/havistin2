
import taxa.common as common

def get_obs_aggregate_data(qname):
    limit = 100

    # counts etc.
    # https://api.laji.fi/v0/warehouse/query/unit/list?selected=gathering.notes%2Cunit.abundanceString%2Cunit.abundanceUnit%2Cunit.identifications.notes%2Cunit.notes&pageSize=100&page=1&cache=false&taxonId=MX.230528&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&individualCountMin=1&qualityIssues=NO_ISSUES&access_token=

    # facts
    # https://api.laji.fi/v0/warehouse/query/unit/list?selected=gathering.facts.decimalValue%2Cgathering.facts.fact%2Cgathering.facts.integerValue%2Cgathering.facts.value%2Cunit.facts.decimalValue%2Cunit.facts.fact%2Cunit.facts.integerValue%2Cunit.facts.value&pageSize=100&page=1&cache=false&taxonId=MX.230528&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&individualCountMin=1&qualityIssues=NO_ISSUES&access_token=

    species_data = common.fetch_finbif_api(f"https://api.laji.fi/v0/warehouse/query/unit/list?pageSize={limit}&page=1&cache=true&taxonId={qname}&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&individualCountMin=1&qualityIssues=NO_ISSUES&access_token=")

    return species_data


def main(taxon_id_untrusted):

    qname = common.valid_qname(taxon_id_untrusted)
    
    html = dict()

    # Get basic taxon data
    # &selectedFields=id,vernacularName,scientificName,typeOfOccurrenceInFinland,parent.family.scientificName,observationCountFinland
    species_data = common.fetch_finbif_api(f"https://api.laji.fi/v0/taxa/{qname}/species?onlyFinnish=true&lang=fi&page=1&pageSize=10&sortOrder=taxonomic&access_token=")

    # Expecting only one species
    html["raw_data"] = species_data["results"][0]

    common.print_log(species_data)

    html["occurrence_status"] = common.fetch_variable_label(html["raw_data"]["typeOfOccurrenceInFinland"][0])

    html["primary_habitat"] = common.fetch_variable_label(html["raw_data"]["primaryHabitat"]["habitat"])

    html["redlist_status"] = common.fetch_variable_label(html["raw_data"]["latestRedListStatusFinland"]["status"])
    html["redlist_year"] = html["raw_data"]["latestRedListStatusFinland"]["year"]

    html["raw_occurrences"] = get_obs_aggregate_data(qname)


#    html["scientific_name"] = species_data["scientificName"]
#    html["obs_count_finland"] = species_data["observationCountFinland"]


    return html
