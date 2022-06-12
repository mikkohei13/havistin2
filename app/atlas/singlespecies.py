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

def main(species_name_untrusted):
    species_name = valid_species_name(species_name_untrusted)

    all_species_pairs = read_json_to_dict("species-pairs.json")
    species_pairs = all_species_pairs[species_name]

    html = dict()
    html["species_name"] = species_name
    html["species_pairs"] = species_pairs["pareja"]

    return html
