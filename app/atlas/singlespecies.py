import re
import json

import atlas.common as common

def valid_species_name(species_name_untrusted):    
    pattern = r"[a-zA-ZäöÄÖ]+"
    match = re.fullmatch(pattern, species_name_untrusted)

    if match is not None:
        species_name = species_name_untrusted.lower()
#        species_name = species_name.capitalize()
        return species_name
    else:
        common.print_log("ERROR: Lajinimi ei kelpaa")
        raise ValueError

def read_json_to_dict(filename):
    filename = "./data/" + filename
    f = open(filename)       
    dictionary = json.load(f)
    f.close()
    return dictionary


def get_confirmed_atlascode_counts(taxon_id):
    # TODO: add quality classes
    time = "2022%2F2025"
    time = "2000%2F2025"

    url = f"https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=unit.atlasCode&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=100&page=1&cache=true&taxonId={taxon_id}&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&time={time}&individualCountMin=1&qualityIssues=NO_ISSUES&atlasClass=MY.atlasClassEnumD&access_token=";

    data_dict = common.fetch_finbif_api(url)
    common.print_log(data_dict) # debug

    html = "<table class='styled-table'>"
    html += "<thead><tr><th>Pesimävarmuusindeksi</th><th>Havaintoja kpl</th></tr></thead>"

    for item in data_dict["results"]:
        atlas_code = item["aggregateBy"]["unit.atlasCode"]

        # Skip inaccurate atlas code's
        if "http://tun.fi/MY.atlasCodeEnum7" == atlas_code:
            continue
        if "http://tun.fi/MY.atlasCodeEnum8" == atlas_code:
            continue

        html += "\n<tr><td>" + common.atlas_code_to_text(atlas_code) + "</td>"
        html += "<td>" + str(item["count"]) + "</td></tr>"

    html += "</table>"
    return html


def get_atlasclass_counts(taxon_id):
    # TODO: add quality classes
    url = f"https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=unit.atlasClass&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=100&page=1&cache=true&taxonId={taxon_id}&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&time=2022%2F2025&individualCountMin=1&qualityIssues=NO_ISSUES&access_token=";

    data_dict = common.fetch_finbif_api(url)

    html = "<table class='styled-table'>"
    html += "<thead><tr><th>Pesimävarmuusluokka</th><th>Havaintoja kpl</th></tr></thead>"
    total = 0

    for item in data_dict["results"]:
        if "http://tun.fi/MY.atlasClassEnumB" == item["aggregateBy"]["unit.atlasClass"]:
            html += "<tr><td>Mahdollinen</td>"
            html += "<td>" + str(item["count"]) + "</td></tr>"
            total = total + item["count"]
        elif "http://tun.fi/MY.atlasClassEnumC" == item["aggregateBy"]["unit.atlasClass"]:
            html += "<tr><td>Todennäköinen</td>"
            html += "<td>" + str(item["count"]) + "</td></tr>"
            total = total + item["count"]
        elif "http://tun.fi/MY.atlasClassEnumD" == item["aggregateBy"]["unit.atlasClass"]:
            html += "<tr><td>Varma</td>"
            html += "<td>" + str(item["count"]) + "</td></tr>"
            total = total + item["count"]

    html += f"<tr><td><strong>Yhteensä</strong></td><td><strong>{total}</strong></td></tr>\n"
    html += "</table>"

    return html, total


def main(species_name_untrusted):
    species_name = valid_species_name(species_name_untrusted)

    all_species_data = read_json_to_dict("species-data.json")
    species_data = all_species_data.get(species_name, False)

    if not species_data:
        common.print_log("ERROR: Species not found: " + species_name)
        raise ValueError

    all_species_pairs = read_json_to_dict("species-pairs.json")
    species_pairs_dict = all_species_pairs.get(species_name, { "pareja": 0 })
    species_pairs = species_pairs_dict["pareja"]

    if not isinstance(species_pairs, int):
        species_pairs = int(float(species_pairs.replace(",", ".")))

    atlas_classes_html, observations_total = get_atlasclass_counts(species_data["id"])

    if 0 == species_pairs:
        proportion = "(ei voi laskea)"
    else:
        proportion = round(observations_total / species_pairs, 4)

#    common.print_log(species_data) # debug

    confirmed_atlas_codes = get_confirmed_atlascode_counts(species_data["id"])

    html = dict()
    html["species_name"] = species_name
    html["species_pairs"] = species_pairs
    html["redlist"] = species_data["redlist"]
    html["habitats"] = species_data["habitats"]
    html["atlas_classes_html"] = atlas_classes_html
    html["proportion"] = proportion
    html["confirmed_atlas_codes_html"] = confirmed_atlas_codes

    


    return html
