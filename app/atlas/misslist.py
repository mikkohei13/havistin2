from xml.sax.handler import property_dom_node
import requests
import json

from datetime import datetime, date, timedelta

import finnish_species
import atlas.common as common


def atlas_species():
    filename = "./data/atlas-species.json"
    f = open(filename)       

    species_dict = json.load(f)

    f.close()
    return species_dict


def add_species_to_pointsdict(pointsdict, square_id):
    newsquare_species_dict, newsquare_species_info = common.get_atlas4_square_data(square_id)

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


def species_html():

    '''
    html = "<div id='listwrapper'>"
    html += "<div class='row header'><div class='species'>Laji</div><div class='atlas3'>3.</div><div class='atlas4'>4.</div><div class='own'>Oma hav.</div></div>"

#    for speciesFi in all_species_dict:
    for speciesFi in finnish_species.list:
        # all_species_dict['speciesFi']

        if speciesFi in species_to_show_dict:

            row_class = ""

            # Atlas 3 data
            atlas3_class = "&nbsp;"
            atlas3_code = "&nbsp;"
            if speciesFi in atlas3_species_dict:
                atlas3_class = convert_atlasclass(atlas3_species_dict[speciesFi]["breedingCategory"])
                atlas3_code = str(atlas3_species_dict[speciesFi]["breedingIndex"]).replace("0", "")

            row_class += f" atlas3_class_{atlas3_class}"

            # Atlas 4 data
            atlas4_class = "&nbsp;"
            atlas4_code = "&nbsp;"
            if speciesFi in atlas4_species_dict:
                atlas4_class = convert_atlasclass(atlas4_species_dict[speciesFi]["atlasClass"]["value"])
                atlas4_code = str(split_atlascode(atlas4_species_dict[speciesFi]["atlasCode"]["value"]))

            row_class += f" atlas4_class_{atlas4_class}"

            # Breeding species
            if speciesFi in breeding_species_list:
                row_class += " breeding_now"
            else:
                row_class += " "

            # HTML
            html += f"<div class='row {row_class}'>"
            html += f"<div class='species'>{speciesFi}</div>"
            html += f"<div class='atlas3'>{atlas3_class}</div>"
            html += f"<div class='atlas4'>{atlas4_code}</div>"
            html += "<div class='own'>&nbsp;</div>"

            html += "</div>"

    html += "</div>"
    '''

    html = "HERE"

    return html


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

    square_id = common.valid_square_id(square_id_untrusted)
    html["square_id"] = square_id

    around_ids = common.neighbour_ids(square_id, True)
    html["neighbour_ids"] = around_ids

    # Atlas 4
    atlas4_species_dict, atlas4_square_info_dict = common.get_atlas4_square_data(square_id)

    html["title"] = f"Atlasruudun {atlas4_square_info_dict['coordinates']} puutelista"
    html["species"] = species_html()

    html["heading"] = f"{atlas4_square_info_dict['coordinates']} {atlas4_square_info_dict['name']} <span> - {atlas4_square_info_dict['birdAssociationArea']['value']}</span>"
    
    html["info_top"] = common.get_info_top_html(atlas4_square_info_dict)

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


