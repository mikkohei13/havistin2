
import taxa.common_taxa as common_taxa
from helpers import common_helpers

def get_obs_aggregate_data(qname):
    limit = 10000

    # counts etc.
    # https://api.laji.fi/v0/warehouse/query/unit/list?selected=gathering.notes%2Cunit.abundanceString%2Cunit.abundanceUnit%2Cunit.identifications.notes%2Cunit.notes&pageSize=100&page=1&cache=true&taxonId=MX.230528&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&individualCountMin=1&qualityIssues=NO_ISSUES&access_token=

    # facts
    # https://api.laji.fi/v0/warehouse/query/unit/list?selected=gathering.facts.decimalValue%2Cgathering.facts.fact%2Cgathering.facts.integerValue%2Cgathering.facts.value%2Cunit.facts.decimalValue%2Cunit.facts.fact%2Cunit.facts.integerValue%2Cunit.facts.value&pageSize=100&page=1&cache=true&taxonId=MX.230528&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&individualCountMin=1&qualityIssues=NO_ISSUES&access_token=

    # To exclude iNat for development: &collectionIdNot=HR.3211
    obs_data = common_helpers.fetch_finbif_api(f"https://api.laji.fi/v0/warehouse/query/unit/list?selected=gathering.facts.decimalValue%2Cgathering.facts.fact%2Cgathering.facts.integerValue%2Cgathering.facts.value%2Cunit.facts.decimalValue%2Cunit.facts.fact%2Cunit.facts.integerValue%2Cunit.facts.value&pageSize={ limit }&page=1&cache=true&taxonId={ qname }&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&individualCountMin=1&qualityIssues=NO_ISSUES&access_token=", True)

    #TODO: override gathering facts by unit facts

    facts_dict = dict()

    # Observations
    for obs in obs_data["results"]:
#        common_helpers.print_log("NEW OBS")
#        common_helpers.print_log(obs)
        this_obs_facts = dict()

        # TODO: Gathering facts

        # Unit facts
        if "unit" in obs:
            unit = obs["unit"]
#            common_helpers.print_log("unit:")
#            common_helpers.print_log(unit)
            if "facts" in unit:
                for unit_fact in unit["facts"]:
#                    common.print_log("unit_fact:")
#                    common_helpers.print_log(unit_fact)
                    # For unknown reason, trying to capitalize some values result in error, even that all values should be strings
                    if "http://tun.fi/MY.hostInformalNameString" == unit_fact["fact"]:
                        this_obs_facts[unit_fact["fact"]] = unit_fact["value"].capitalize()
                    else:
                        this_obs_facts[unit_fact["fact"]] = unit_fact["value"]

#        common_helpers.print_log(this_obs_facts)

        for key, value in this_obs_facts.items():
            if key in facts_dict:
                facts_dict[key].append(value)
            else:
                facts_dict[key] = []
                facts_dict[key].append(value)


#    common_helpers.print_log("==================")
#    common_helpers.print_log(facts_dict)

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


def summarize_fact(data, name, fetch_terms):
    summary = dict()
    for item in data:
        if item not in summary:
            summary[item] = 1
        else:
            summary[item] = summary[item] + 1

    # Sort by value desc
    summary = dict(sorted(summary.items(), key=lambda item: item[1], reverse=True))

    if fetch_terms:
        summary_human_readable = dict()
        for key, value in summary.items():
            summary_human_readable[common_taxa.fetch_variable_label(key)] = value
    else:
        summary_human_readable = summary

    html = "<table class='styled-table facts'>\n"
    html += f"<thead><th>{name}</th><th>Havaintoja kpl</th></thead>\n"
    html += "<tbody>\n"
    for key, value in summary_human_readable.items():
        html += f"<tr><td>{key}</td><td>{value}</td></tr>\n"
    html += "</tbody>\n</table>\n"

    return html


def main(taxon_id_untrusted):

    qname = common_taxa.valid_qname(taxon_id_untrusted)
    
    html = dict()

    # 1) Get basic species data
    url = f"https://api.laji.fi/v0/taxa/{qname}/species?onlyFinnish=true&lang=fi&page=1&pageSize=10&sortOrder=taxonomic&access_token="
    species_data = common_helpers.fetch_finbif_api(url, True)

    # Handling only one species, so pick the first result
    html["raw_data"] = species_data["results"][0]

    # Get species information that is available on the basic taxon data
    if "occurrence_status" in html["raw_data"]:
        html["occurrence_status"] = common_taxa.fetch_variable_label(html["raw_data"]["typeOfOccurrenceInFinland"][0])
    else:
        html["occurrence_status"] = "Ei statustietoa"

    if "primary_habitat" in html["raw_data"]:
        html["primary_habitat"] = common_taxa.fetch_variable_label(html["raw_data"]["primaryHabitat"]["habitat"])
    else:
        html["primary_habitat"] = ""

    if "redlist_status" in html["raw_data"]:
        html["redlist_status"] = common_taxa.fetch_variable_label(html["raw_data"]["latestRedListStatusFinland"]["status"])
        html["redlist_year"] = html["raw_data"]["latestRedListStatusFinland"]["year"]

    # 2) Get additional data by fethcing top n (10.000) observations
    raw_facts = get_obs_aggregate_data(qname)
#    common_helpers.print_log(raw_facts)

    html["fact_table"] = generate_fact_table(raw_facts)

    if "http://tun.fi/MY.samplingMethod" in raw_facts:
        html["samplingMethod"] = summarize_fact(raw_facts['http://tun.fi/MY.samplingMethod'], "Keruumenetelmä", True)

    if "http://tun.fi/MY.lifeStage" in raw_facts:
        html["lifeStage"] = summarize_fact(raw_facts['http://tun.fi/MY.lifeStage'], "Elinvaihe", True)

    if "http://tun.fi/MY.hostInformalNameString" in raw_facts:
        html["hostInformalNameString"] = summarize_fact(raw_facts['http://tun.fi/MY.hostInformalNameString'], "Isäntälaji (vapaateksti)", False)

    if "http://tun.fi/MY.habitatIUCN" in raw_facts:
        html["habitatIUCN"] = summarize_fact(raw_facts['http://tun.fi/MY.habitatIUCN'], "Habitaatti", False)

    if "http://tun.fi/MY.habitatDescription" in raw_facts:
        html["habitatDescription"] = summarize_fact(raw_facts['http://tun.fi/MY.habitatDescription'], "Habitaatin kuvaus", False)


#    html["scientific_name"] = species_data["scientificName"]
#    html["obs_count_finland"] = species_data["observationCountFinland"]


    return html
