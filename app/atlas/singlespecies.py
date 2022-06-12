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

    atlas_codes = dict()

    for item in data_dict["results"]:
        atlas_codes[item["aggregateBy"]["unit.atlasCode"]] = item["count"]

    return atlas_codes


def get_atlasclass_counts(taxon_id):
    # TODO: add quality classes
    url = f"https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=unit.atlasClass&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=100&page=1&cache=true&taxonId={taxon_id}&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&time=2022%2F2025&individualCountMin=1&qualityIssues=NO_ISSUES&access_token=";

    data_dict = common.fetch_finbif_api(url)

    atlas_classes = dict()
    total = 0

    for item in data_dict["results"]:
        if "http://tun.fi/MY.atlasClassEnumB" == item["aggregateBy"]["unit.atlasClass"]:
            atlas_classes["possible"] = item["count"]
            total = total + item["count"]
        elif "http://tun.fi/MY.atlasClassEnumC" == item["aggregateBy"]["unit.atlasClass"]:
            atlas_classes["probable"] = item["count"]
            total = total + item["count"]
        elif "http://tun.fi/MY.atlasClassEnumD" == item["aggregateBy"]["unit.atlasClass"]:
            atlas_classes["confirmed"] = item["count"]
            total = total + item["count"]

    atlas_classes["total"] = total

    return atlas_classes


def main(species_name_untrusted):
    species_name = valid_species_name(species_name_untrusted)

    all_species_data = read_json_to_dict("species-data.json")
    species_data = all_species_data.get(species_name, False)

    if not species_data:
        common.print_log("ERROR: Species not found: " + species_name)
        raise ValueError

    all_species_pairs = read_json_to_dict("species-pairs.json")
    species_pairs = all_species_pairs.get(species_name, { "pareja": 0 })

    atlas_classes = get_atlasclass_counts(species_data["id"])

    if 0 == species_pairs:
        proportion = "(ei voi laskea)"
    else:
        proportion = round(atlas_classes["total"] / species_pairs["pareja"], 4)

#    common.print_log(species_data) # debug

    confirmed_atlas_codes = get_confirmed_atlascode_counts(species_data["id"])

    html = dict()
    html["species_name"] = species_name
    html["species_pairs"] = species_pairs["pareja"]
    html["redlist"] = species_data["redlist"]
    html["habitats"] = species_data["habitats"]
    html["atlas_classes"] = atlas_classes
    html["proportion"] = proportion
    html["confirmed_atlas_codes"] = confirmed_atlas_codes

    


    return html
