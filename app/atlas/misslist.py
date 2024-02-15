from xml.sax.handler import property_dom_node
#import requests
import json

from datetime import datetime, date, timedelta

#import finnish_species
import atlas.common_atlas as common_atlas
from helpers import common_helpers


def make_misstable(sorted_missvalues, atlas4_species):
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
    species_predictions = common_atlas.get_species_predictions(square_id, 2024)

    # Calculate missvalues
    missvalues = common_atlas.get_species_missvalues(species_predictions, atlas4_species)
    sorted_missvalues = {k: v for k, v in sorted(missvalues.items(), key=lambda item: item[1], reverse=True)}
#    print(sorted_missvalues)

    # Generate HTML
    html["species_table"] = make_misstable(sorted_missvalues, atlas4_species)
    html["title"] = f"Atlasruudun {atlas4_square_info['coordinates']} puutelista"
    html["heading"] = f"{atlas4_square_info['coordinates']} {atlas4_square_info['name']} <span> - {atlas4_square_info['birdAssociationArea']['value']}</span>"
    html["info_top"] = common_atlas.get_info_top_html(atlas4_square_info)

    return html


