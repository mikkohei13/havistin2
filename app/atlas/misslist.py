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


# TODO: Move to common
def convert_breeding_number(atlas_class_key):
    if "MY.atlasClassEnumA" == atlas_class_key:
        return 0
    if "MY.atlasClassEnumB" == atlas_class_key:
        return 1
    if "MY.atlasClassEnumC" == atlas_class_key:
        return 2
    if "MY.atlasClassEnumD" == atlas_class_key:
        return 3

# TODO: move to common
def atlas4_square(square_id):
    square_id = square_id.replace(":", "%3A")
    url = f"https://atlas-api.rahtiapp.fi/api/v1/grid/{square_id}/atlas"

    req = requests.get(url)
    data_dict = req.json()

    # Square metadata as separate dict, without species
    square_info_dict = data_dict.copy()
    square_info_dict.pop("data", None)

    # Species dict with fi name as key
    species_dict = dict().copy()
    breeding_sum_counter = 0

    for species in data_dict["data"]:
        species_dict[species["speciesName"]] = species
        breeding_sum_counter = breeding_sum_counter + convert_breeding_number(species["atlasClass"]["key"])

    square_info_dict["breeding_sum"] = breeding_sum_counter

    return species_dict, square_info_dict


def add_species_to_pointsdict(pointsdict, square_id):
    newsquare_species_dict, newsquare_species_info = atlas4_square(square_id)

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

# Todo: Move to common
def split_atlascode(atlascode_text):
    parts = atlascode_text.split(" ")
    return parts[0]
    
# Todo: Move to common
def convert_atlasclass(atlasclass_raw):
    if atlasclass_raw == "Epätodennäköinen pesintä" or atlasclass_raw == 1:
        return "e"
    elif atlasclass_raw == "Mahdollinen pesintä" or atlasclass_raw == 2:
        return "M"
    elif atlasclass_raw == "Todennäköinen pesintä" or atlasclass_raw == 3:
        return "T"
    elif atlasclass_raw == "Varma pesintä" or atlasclass_raw == 4:
        return "V"
    else:
        return atlasclass_raw


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

# TODO: Move to common
def info_top_html(atlas4_square_info_dict):

    level2 = round(atlas4_square_info_dict['level2'], 1)
    level3 = round(atlas4_square_info_dict['level3'], 1)
    level4 = round(atlas4_square_info_dict['level4'], 1)
    level5 = round(atlas4_square_info_dict['level5'], 1)

    if atlas4_square_info_dict['breeding_sum'] >= atlas4_square_info_dict['level5']:
        current_level = "erinomainen"
    elif atlas4_square_info_dict['breeding_sum'] >= atlas4_square_info_dict['level4']:
        current_level = "hyvä"
    elif atlas4_square_info_dict['breeding_sum'] >= atlas4_square_info_dict['level3']:
        current_level = "tyydyttävä"
    elif atlas4_square_info_dict['breeding_sum'] >= atlas4_square_info_dict['level2']:
        current_level = "välttävä"
    elif atlas4_square_info_dict['breeding_sum'] >= atlas4_square_info_dict['level1']:
        current_level = "satunnaishavaintoja"
    else:
        current_level = "ei havaintoja"
    
    square_id = atlas4_square_info_dict["coordinates"]

    html = ""
    html += f"<p id='paragraph3'>Selvitysaste: {current_level}, summa: {atlas4_square_info_dict['breeding_sum']} (rajat: välttävä {level2}, tyydyttävä {level3}, hyvä {level4}, erinomainen {level5})</p>"

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
    html += "<thead><tr><th>Laji</th><th>Pistearvo</th><th>Korkein indeksi</th></tr></thead><tbody>"

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
    atlas4_species_dict, atlas4_square_info_dict = atlas4_square(square_id)

    html["title"] = f"Atlasruudun {atlas4_square_info_dict['coordinates']} puutelista"
    html["species"] = species_html()

    html["heading"] = f"{atlas4_square_info_dict['coordinates']} {atlas4_square_info_dict['name']} <span> - {atlas4_square_info_dict['birdAssociationArea']['value']}</span>"
    
    # TODO: Move to common
    html["info_top"] = info_top_html(atlas4_square_info_dict)

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
#    common.print_log(filtered_pointsdict)

    html["species_table"] = make_table(filtered_pointsdict)

    return html


