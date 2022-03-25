import requests
import json

from flask import request

import json
import sys

import app_secrets

def print_r(dict):
    print("DICT:", file = sys.stdout)
#    print(*dict.items(), sep="\n", file = sys.stdout)
    print(dict, sep="\n", file = sys.stdout)


def print_debug(data):
    print("DEBUG:", file = sys.stdout)
    print(str(data), file = sys.stdout)


def atlas3_to_dict(square_id):
    filename = "./data/atlas3/" + square_id.replace(":", "-") + ".json"   
    f = open(filename)

    species_dict = json.load(f)
    
    f.close()
    return species_dict


def atlas4_square(square_id):
    square_id = square_id.replace(":", "%3A")
    url = "https://atlas-api.rahtiapp.fi/api/v1/grid/" + square_id + "/atlas"

    req = requests.get(url)
    data_dict = req.json()

    # Square metadata as separate dict, without species
    square_info_dict = data_dict.copy()
    square_info_dict.pop("data", None)

    # Species dict with fi name as key
    species_dict = dict().copy()

    for species in data_dict["data"]:
        species_dict[species["speciesName"]] = species

    return species_dict, square_info_dict


def split_atlascode(atlascode_value):
    parts = atlascode_value.split(" ")
    return parts[0]
    

def generate_species_table(atlas3_species_dict, atlas4_species_dict):

    html_table = "<table>"
    html_table += "<tr><td>Laji</td><td>3. atlas</td><td>4. atlas</td><td>Oma havainto</td></tr>"

    for species in atlas3_species_dict:
        print_r(species)
        speciesFi = species["speciesFi"]

        html_table += "<tr>"
        html_table += "<td>" + speciesFi + "</td>"

        # Atlas 3 data
        html_table += "<td>" + str(species["breedingIndex"]).replace("0", "") + "</td>"

        # Atlas 4 data
        atlas4_class = ""
        atlas4_code = ""
        if speciesFi in atlas4_species_dict:
            atlas4_class = str(atlas4_species_dict[speciesFi]["atlasClass"]["value"])
            atlas4_code = str(split_atlascode(atlas4_species_dict[speciesFi]["atlasCode"]["value"]))

        html_table += "<td>" + atlas4_code + "</td>"

        # Own observation
        html_table += "<td>&nbsp;</td>"

        html_table += "</tr>"

    html_table += "</table>"

    return html_table



def main():
    square_id = request.args.get("id", default="", type=str)

    # TODO: sanitize input

    atlas3_species_dict = atlas3_to_dict(square_id)
    print_r(atlas3_species_dict)

    atlas4_species_dict, atlas4_square_info_dict = atlas4_square(square_id)

    html_table = generate_species_table(atlas3_species_dict, atlas4_species_dict)

    html_heading = ""
    html_heading += "<h1>" + atlas4_square_info_dict["coordinates"] + " " + atlas4_square_info_dict["name"] + "</h1>"
    html_heading += "<p>" + atlas4_square_info_dict["birdAssociationArea"]["value"] + "</p>"

    return html_table, html_heading
