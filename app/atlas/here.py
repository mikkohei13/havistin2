
from dataclasses import replace
#import json
import atlas.common_atlas as common_atlas
from helpers import common_helpers


'''
def observation_coordinates(square_id):
    url = f"https://api.laji.fi/v0/warehouse/query/unit/list?selected=gathering.conversions.wgs84CenterPoint.lat%2Cgathering.conversions.wgs84CenterPoint.lon%2Cgathering.coordinatesVerbatim&pageSize=1000&page=1&cache=false&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&time=2022%2F2025&individualCountMin=1&coordinates={square_id}%3AYKJ&qualityIssues=NO_ISSUES&atlasClass=MY.atlasClassEnumB%2CMY.atlasClassEnumC%2CMY.atlasClassEnumD&coordinateAccuracyMax=5000&access_token=";

    data_dict = common_helpers.fetch_finbif_api(url)

    obs_count = data_dict["total"] 

    coord_string = ""
    for obs in data_dict["results"]:
        # Todo: skip those with just center coordinates
        #    if (isset($obs['gathering']['coordinatesVerbatim'])) {
        lat = obs['gathering']['conversions']['wgs84CenterPoint']['lat']
        lon = obs['gathering']['conversions']['wgs84CenterPoint']['lon']
        coord_string = coord_string + f"[{lat},{lon}],\n"

    return coord_string, obs_count
'''


def make_misstable(sorted_missvalues, atlas4_species):
    html = "<table class='styled-table'>"
    html += "<thead><tr><th>Laji</th><th>Puute</th><th>Max</th></tr></thead><tbody>"

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
            html += "<tr class='hard'>"

        html += f"<td>{species}</td>"
        html += f"<td>{ missvalue }</td>"

        if species not in atlas4_species:
            html += f"<td class='atlas_code'>&nbsp;</td>"        
        else:
            breeding_index = atlas4_species[species]['atlasCode']['key'].replace("MY.atlasCodeEnum", "")
            html += f"<td class='atlas_code'>{ breeding_index }</td>"

        html += "</tr>\n"

    html += "</tbody></table>"

    return html


def make_biotopetable(biotope_values):
    html = "<table class='styled-table'>"
    html += "<thead><tr><th>Laji</th><th>Puute</th></tr></thead><tbody>"

    for biotope_abbr, biotope_value in biotope_values.items():
        biotope = "muu"
        if "p" == biotope_abbr:
            biotope = "maaseutu- ja rakennetut ympäristöt"
        if "m" == biotope_abbr:
            biotope = "metsät"
        if "v" == biotope_abbr:
            biotope = "vesistöt"
        if "t" == biotope_abbr:
            biotope = "tunturipaljakka"
        if "s" == biotope_abbr:
            biotope = "avosuot"

        biotope_value = round(biotope_value, 1)

        html += "<tr>\n"
        html += f"<td>{ biotope }</td>"
        html += f"<td>{ biotope_value }</td>"
        html += "</tr>\n"

    html += "</tbody></table>"

    return html


def calculate_biotope_values(sorted_missvalues, species_biotopes):
    biotope_values = dict()
    for species, missvalue in sorted_missvalues.items():

        species_data = species_biotopes[species]

        # Skip if species does not have biotope value
        if "bio" not in species_data:
            continue

        biotope = species_data["bio"]

        # Init empty biotope values
        if biotope not in biotope_values:
            biotope_values[biotope] = 0

        # Add raw biotope value
        biotope_values[biotope] = biotope_values[biotope] + missvalue

    biotope_values = {k: v for k, v in sorted(biotope_values.items(), key=lambda item: item[1], reverse=True)}
    return biotope_values


def main(square_id_untrusted):
    html = dict()

    # Get basic info about the square
    square_id = common_atlas.valid_square_id(square_id_untrusted)
    html["square_id"] = square_id

    coordinate_accuracy_data, total_obs_count = common_atlas.coordinate_accuracy_data(square_id)

    square_name, society, centerpoint, cornerpoints = common_atlas.square_info(square_id)

    # Get atlas 4 data
    atlas4_species, atlas4_square_info = common_atlas.get_atlas4_square_data(square_id)

    # Get prediction data
    species_predictions = common_atlas.get_species_predictions(square_id, 2024)

    # Calculate missvalues
    missvalues = common_atlas.get_species_missvalues(species_predictions, atlas4_species)
    sorted_missvalues = {k: v for k, v in sorted(missvalues.items(), key=lambda item: item[1], reverse=True)}
    print(sorted_missvalues)

    # Get biotope data
    species_biotopes = common_atlas.read_json_to_dict("species-data.json")

#    print(sorted_missvalues)

    biotope_values = calculate_biotope_values(sorted_missvalues, species_biotopes)
    html["biotope_table"] = make_biotopetable(biotope_values)


    # Generate HTML
    html["species_table"] = make_misstable(sorted_missvalues, atlas4_species)
#    html["heading"] = f"{atlas4_square_info['coordinates']} {atlas4_square_info['name']} <span> - {atlas4_square_info['birdAssociationArea']['value']}</span>"
    html["info_top"] = common_atlas.get_info_top_html(atlas4_square_info)

    html["society"] = society
    html["observation_count"] = total_obs_count
    html["square_id"] = f"{square_id}"
    html["heading"] = f"{square_id} {square_name}"
    html["centerpoint"] = centerpoint
    html["cornerpoints"] = cornerpoints



    return html
