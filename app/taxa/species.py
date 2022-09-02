
import taxa.common as common

def get_obs_aggregate_data(qname):
    limit = 10000

    # counts etc.
    # https://api.laji.fi/v0/warehouse/query/unit/list?selected=gathering.notes%2Cunit.abundanceString%2Cunit.abundanceUnit%2Cunit.identifications.notes%2Cunit.notes&pageSize=100&page=1&cache=false&taxonId=MX.230528&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&individualCountMin=1&qualityIssues=NO_ISSUES&access_token=

    # facts
    # https://api.laji.fi/v0/warehouse/query/unit/list?selected=gathering.facts.decimalValue%2Cgathering.facts.fact%2Cgathering.facts.integerValue%2Cgathering.facts.value%2Cunit.facts.decimalValue%2Cunit.facts.fact%2Cunit.facts.integerValue%2Cunit.facts.value&pageSize=100&page=1&cache=false&taxonId=MX.230528&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&individualCountMin=1&qualityIssues=NO_ISSUES&access_token=

    # Note: iNat excluded for development
    obs_data = common.fetch_finbif_api(f"https://api.laji.fi/v0/warehouse/query/unit/list?selected=gathering.facts.decimalValue%2Cgathering.facts.fact%2Cgathering.facts.integerValue%2Cgathering.facts.value%2Cunit.facts.decimalValue%2Cunit.facts.fact%2Cunit.facts.integerValue%2Cunit.facts.value&pageSize={limit}&page=1&cache=false&taxonId={qname}&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&collectionIdNot=HR.3211&individualCountMin=1&qualityIssues=NO_ISSUES&access_token=", True)

    #TODO: override gathering facts by unit facts

    facts_dict = dict()

    # Observations
    for obs in obs_data["results"]:
        common.print_log("NEW OBS")
        common.print_log(obs)
        this_obs_facts = dict()

        # TODO: Gathering facts

        # Unit facts
        if "unit" in obs:
            unit = obs["unit"]
            common.print_log("unit:")
            common.print_log(unit)
            if "facts" in unit:
                for unit_fact in unit["facts"]:
                    common.print_log("unit_fact:")
                    common.print_log(unit_fact)
                    this_obs_facts[unit_fact["fact"]] = unit_fact["value"]

        common.print_log(this_obs_facts)

        for key, value in this_obs_facts.items():
            if key in facts_dict:
                facts_dict[key].append(value)
            else:
                facts_dict[key] = []
                facts_dict[key].append(value)


    common.print_log("==================")
    common.print_log(facts_dict)

    return facts_dict


def generate_fact_table(facts_dict):
    html = "<table class='styled-table'>"
    for key, value in facts_dict.items():
        html += "<tr>"
        html += f"<td>{key}</td>"
        html += f"<td>{value}</td>"
        html += "</tr>"
    html += "</table>"

    return html




def main(taxon_id_untrusted):

    qname = common.valid_qname(taxon_id_untrusted)
    
    html = dict()

    # Get basic taxon data
    # &selectedFields=id,vernacularName,scientificName,typeOfOccurrenceInFinland,parent.family.scientificName,observationCountFinland
    species_data = common.fetch_finbif_api(f"https://api.laji.fi/v0/taxa/{qname}/species?onlyFinnish=true&lang=fi&page=1&pageSize=10&sortOrder=taxonomic&access_token=")

    # TODO: Better var names
    # Expecting only one species
    html["raw_data"] = species_data["results"][0]

    html["occurrence_status"] = common.fetch_variable_label(html["raw_data"]["typeOfOccurrenceInFinland"][0])

    if "primary_habitat" in html["raw_data"]:
        html["primary_habitat"] = common.fetch_variable_label(html["raw_data"]["primaryHabitat"]["habitat"])
    else:
        html["primary_habitat"] = ""

    if "redlist_status" in html["raw_data"]:
        html["redlist_status"] = common.fetch_variable_label(html["raw_data"]["latestRedListStatusFinland"]["status"])
        html["redlist_year"] = html["raw_data"]["latestRedListStatusFinland"]["year"]

    raw_facts = get_obs_aggregate_data(qname)
    html["fact_table"] = generate_fact_table(raw_facts)


#    html["scientific_name"] = species_data["scientificName"]
#    html["obs_count_finland"] = species_data["observationCountFinland"]


    return html
