from xml.sax.handler import property_dom_node
#import requests
import json

from datetime import datetime, date, timedelta

#import finnish_species
import atlas.common_atlas as common_atlas
from helpers import common_helpers


def make_table(sorted_missvalues, atlas4_species):
    html = "<table class='styled-table'>"
    html += "<thead><tr><th>Laji</th><th>Pistearvo</th><th>Korkein indeksi tällä ruudulla</th></tr></thead><tbody>"

    for species, missvalue in sorted_missvalues.items():

        # Skip confirmed breeders
        if species in atlas4_species:
            if "MY.atlasClassEnumD" == atlas4_species[species]['atlasClass']['key']:
                continue

        if species not in atlas4_species:
            html += "<tr class='easy'>"
        elif "MY.atlasClassEnumA" == atlas4_species[species]['atlasClass']['key'] or "MY.atlasClassEnumB" == atlas4_species[species]['atlasClass']['key']:
            html += "<tr class='easy'>"
        else:
            html += "<tr>"

        html += f"<td>{species}</td>"
        html += f"<td>{ missvalue }</td>"

        if species not in atlas4_species:
            html += f"<td class='atlas_code'>&nbsp;</td>"        
        else:
            html += f"<td class='atlas_code'>{ atlas4_species[species]['atlasCode']['value'] }</td>"

        html += "</tr>\n"

    html += "</tbody></table>"

    return html


def get_species_predictions(square_id):
    square_filename = square_id.replace(":", "_")
    filename = f"./data/atlas_predictions/{ square_filename }.json"
    f = open(filename)       

    species_dict = json.load(f)

    f.close()
    return species_dict


def atlas_class_to_value(class_value):
    if "MY.atlasClassEnumA" == class_value:
        return 0
    if "MY.atlasClassEnumB" == class_value:
        return 1
    if "MY.atlasClassEnumC" == class_value:
        return 2
    if "MY.atlasClassEnumD" == class_value:
        return 3
    return 0


def get_species_missvalues(species_predictions, atlas4_species):

    # Create new and simpler dictionary of the predicted value
    species_predictions_simple = dict()

    # Count missvalues
    missvalues = dict()

    for species, data in species_predictions.items():

        # Get capped predicted class
        predicted_class = data["predictions"][0]["value"]
        if predicted_class < 0:
            predicted_class = 0
        elif predicted_class > 3:
            predicted_class = 3

        # If observed in 4th atlas, calculate difference
        if species in atlas4_species:
            current_class = atlas_class_to_value(atlas4_species[species]["atlasClass"]["key"])
            missvalue = predicted_class - current_class

            # if already higher than predicted value
            if missvalue < 0:
                missvalue = 0

            missvalue = round(missvalue, 1)
            
        # if not observed, just use predicted value
        else:
            missvalue = round(predicted_class, 1)

        missvalues[species] = missvalue

#        species_predictions_simple[species] = predicted_class

    return missvalues

    for species, current_data in atlas4_species.items():

        # Skip uncommon species
        if species not in species_predictions_simple:
            continue

        current_class = atlas_class_to_value(current_data["atlasClass"]["key"])
        missvalue = species_predictions_simple[species] - current_class
        if missvalue < 0:
            missvalue = 0
        else:
            missvalue = round(missvalue, 2)

        missvalues[species] = missvalue
    
    return missvalues



def main(square_id_untrusted):
    html = dict()

    # Get basic info about the square
    square_id = common_atlas.valid_square_id(square_id_untrusted)
    html["square_id"] = square_id

    around_ids = common_atlas.neighbour_ids(square_id, True)
    html["neighbour_ids"] = around_ids

    # Get atlas 4 data
    atlas4_species, atlas4_square_info = common_atlas.get_atlas4_square_data(square_id)

    # Get prediction data
    species_predictions = get_species_predictions(square_id)

    # Calculate missvalues
    missvalues = get_species_missvalues(species_predictions, atlas4_species)
    sorted_missvalues = {k: v for k, v in sorted(missvalues.items(), key=lambda item: item[1], reverse=True)}
    print(sorted_missvalues)

    # Generate HTML
    html["species_table"] = make_table(sorted_missvalues, atlas4_species)
    html["title"] = f"Atlasruudun {atlas4_square_info['coordinates']} puutelista"
    html["heading"] = f"{atlas4_square_info['coordinates']} {atlas4_square_info['name']} <span> - {atlas4_square_info['birdAssociationArea']['value']}</span>"
    html["info_top"] = common_atlas.get_info_top_html(atlas4_square_info)

    return html


