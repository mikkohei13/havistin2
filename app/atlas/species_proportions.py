
#import json
#from app.main import species_proportions

#from collections import OrderedDict
#from unittest.util import sorted_list_difference
import atlas.common as common

def get_species_atlasobs_counts():
    # TODO: add quality classes
    url = f"https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=unit.linkings.originalTaxon.nameFinnish&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=500&page=1&cache=false&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&taxonRankId=MX.species&countryId=ML.206&time=2022%2F2025&individualCountMin=1&qualityIssues=NO_ISSUES&atlasClass=MY.atlasClassEnumB%2CMY.atlasClassEnumC%2CMY.atlasClassEnumD&access_token=";

    data_dict = common.fetch_finbif_api(url)
    return data_dict


def main():

    species_pairs = common.read_json_to_dict("species-pairs.json")

    species_atlasobs_counts = get_species_atlasobs_counts()
#    common.print_log(species_atlasobs_counts)
#    exit()

    species_proportions = dict()
    species_atlasobs_counts_keyed = dict()

    for item in species_atlasobs_counts["results"]:
        name = item["aggregateBy"]["unit.linkings.originalTaxon.nameFinnish"]
        if name not in species_pairs:
            common.print_log("Name not found: " + name)
            continue
        elif 0 == int(species_pairs[name]["pareja"]):
            continue
        elif name in species_pairs:
            proportion = int(item["count"]) / int(species_pairs[name]["pareja"])
            species_proportions[name] = proportion
            species_atlasobs_counts_keyed[name] = item["count"]
            common.print_log(name + ": ") # debug
            common.print_log(str(proportion) + "\n") # debug

    # Creates list of tuples
    # TODO: Maybe sort on frontend with js instead?
    sorted_species_proportions = sorted(species_proportions.items(), key=lambda item: item[1])
#    common.print_log(sorted_species_proportions)
#    exit()

    species_table_html = "<table class='styled-table'>"
    species_table_html += "<thead><tr><th>Laji</th><th>Havaintoja / pareja</th><th>Pareja / havaintoja<th>Havaintoja</th><th>Pareja (2010)</th></tr></thead><tbody>"

    for species in sorted_species_proportions:
        name = species[0]
        prop = round(species[1], 3)
        prop_invert = round(int(species_pairs[name]['pareja']) / int(species_atlasobs_counts_keyed[name]), 1)

        species_table_html += "<tr>"
        species_table_html += f"<td><a href='/atlas/laji/{name}'>{name}</a></td>"
        species_table_html += f"<td>{prop}</td>"
        species_table_html += f"<td>{prop_invert}</td>"
        species_table_html += f"<td>{species_atlasobs_counts_keyed[name]}</td>"
        species_table_html += f"<td>{species_pairs[name]['pareja']}</td>"
        species_table_html += "</tr>"

    species_table_html += "</tbody></table>"

    '''
    hae kaikkien lajien havaintomäärä (mahd, tn, varma) 4 atlaksesta
    hae kaikkien lajien parimäärä
    foreach laji, 
        havaintomäärä / parimäärä
    '''

    html = dict()
    html["species_table"] = species_table_html

    return html
