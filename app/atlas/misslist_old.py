from xml.sax.handler import property_dom_node
#import requests
import json

from datetime import datetime, date, timedelta

#import finnish_species
import atlas.common_atlas as common_atlas
from helpers import common_helpers


def atlas_species():
    filename = "./data/atlas-species.json"
    f = open(filename)       

    species_dict = json.load(f)

    f.close()
    return species_dict


def add_species_to_pointsdict(pointsdict, square_id):
    newsquare_species_dict, newsquare_species_info = common_atlas.get_atlas4_square_data(square_id)

    # Add points: 3 for confirmed, 2 for probable and 1 for possible breeder
    for key, value in newsquare_species_dict.items():
        species = key
        if species not in pointsdict:
            pointsdict[species] = 0
        if "MY.atlasClassEnumD" == value["atlasClass"]["key"]:
            pointsdict[species] = pointsdict[species] + 3
        elif "MY.atlasClassEnumC" == value["atlasClass"]["key"]:
            pointsdict[species] = pointsdict[species] + 2
        elif "MY.atlasClassEnumB" == value["atlasClass"]["key"]:
            pointsdict[species] = pointsdict[species] + 1

    return pointsdict


def filter_confirmed_species(pointsdict, this_square_species_dict):
    filtered_dict = dict()
#    common.print_log(pointsdict) # debug
#    common.print_log(this_square_species_dict) # debug

    for species, points in pointsdict.items():
        # Skip species which have aleady been confirmed in this square 
        if species in this_square_species_dict:
            if "MY.atlasClassEnumD" == this_square_species_dict[species]["atlasClass"]["key"]:
                continue
        # Add info needed on the page
        filtered_dict[species] = dict()
        filtered_dict[species]["points"] = points

        # If species has been observed in this square:
        if species in this_square_species_dict:
            filtered_dict[species]["atlasCode"] = this_square_species_dict[species]["atlasCode"]["value"]
        # If hasn't been:
        else:
            filtered_dict[species]["atlasCode"] = ""

    return filtered_dict


def make_table(this_square_species):
    html = "<table class='styled-table'>"
    html += "<thead><tr><th>Laji</th><th>Pistearvo</th><th>Korkein indeksi tällä ruudulla</th></tr></thead><tbody>"

    for species, value in this_square_species.items():
        html += f"<td>{species}</td>"
        if not "points" in value:
            value['points'] = "0"
        html += f"<td>{value['points']}</td>"
        html += f"<td>{value['atlasCode']}</td>"
        html += "</tr>\n"

    html += "</tbody></table>"

    return html


def main(square_id_untrusted):
    html = dict()

    square_id = common_atlas.valid_square_id(square_id_untrusted)
    html["square_id"] = square_id

    around_ids = common_atlas.neighbour_ids(square_id, True)
    html["neighbour_ids"] = around_ids

    # Atlas 4
    atlas4_species_dict, atlas4_square_info_dict = common_atlas.get_atlas4_square_data(square_id)

    html["title"] = f"Atlasruudun {atlas4_square_info_dict['coordinates']} puutelista"

    html["heading"] = f"{atlas4_square_info_dict['coordinates']} {atlas4_square_info_dict['name']} <span> - {atlas4_square_info_dict['birdAssociationArea']['value']}</span>"
    
    html["info_top"] = common_atlas.get_info_top_html(atlas4_square_info_dict)

    pointsdict = dict()
    add_species_to_pointsdict(pointsdict, around_ids["n"])
    add_species_to_pointsdict(pointsdict, around_ids["ne"])
    add_species_to_pointsdict(pointsdict, around_ids["e"])
    add_species_to_pointsdict(pointsdict, around_ids["se"])
    add_species_to_pointsdict(pointsdict, around_ids["s"])
    add_species_to_pointsdict(pointsdict, around_ids["sw"])
    add_species_to_pointsdict(pointsdict, around_ids["w"])
    add_species_to_pointsdict(pointsdict, around_ids["nw"])

    filtered_pointsdict = filter_confirmed_species(pointsdict, atlas4_species_dict)

    # Makes a species list that is sorted by points decending
    sorted_species_list = sorted(filtered_pointsdict, reverse=True, key=lambda x: (filtered_pointsdict[x]['points']))

#    common.print_log(sorted_species_list) # debug

    # Create sorted dict
    sorted_pointsdict = dict()
    for species in sorted_species_list:
        sorted_pointsdict[species] = filtered_pointsdict[species]

    html["species_table"] = make_table(sorted_pointsdict)

    return html


