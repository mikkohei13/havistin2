
import atlas.common_atlas as common_atlas
from helpers import common_helpers
import matplotlib.cm as cm
import numpy as np


def text_summap(value, square_id, square_data):
    # Special case for showing target points on the map
    if "tyydyttävä-selvitysaste" == value['atlas_class_name']:
        text = f"{square_id} {square_data['kunta']}, {square_data['nimi']}:<br>Tyydyttävän selvitysasteen raja-arvo: { value['until_level'] }<br>Pesimävarmuussumma nyt: { value['atlas_class_sum'] }"
    else:
        text = f"{square_id} {square_data['kunta']}, {square_data['nimi']}:<br>Pisteitä selvitysasteeseen { value['atlas_class_name'] } tarvitaan: { value['until_level'] }<br>Pesimävarmuussumma nyt: { value['atlas_class_sum'] }"
    return text


def color_viridis_capped(value):
    value = value["until_level"]

    cap = 320 # max value for erinomainen level is 319
    
    # Cap value
    if value > cap:
        value = cap

    # Don't show grids that have reached target value
    opacity = 0.9
    if 0 == value:
        opacity = 0

    # Normalize value to range [0, 1]
    normalized_value = value / cap

    # Get RGB color value along viridis color scale
    #  viridis, inferno, plasma, magma, jet (spectrum), cool, hot
    # Suffix "_r" reverts the scale
    color = cm.viridis_r(normalized_value)

    r, g, b = tuple(np.array(color[:3]) * 255)
    color = f"rgba({round(r,0)}, {round(g,0)}, {round(b,0)}, {opacity})"

    return color


def fetch_breeding_sums(target_class_name, target_class_value):

    target_class_key = f"level{target_class_value}"
    print(target_class_name, target_class_key)

    url = f"https://atlas-api.2.rahtiapp.fi/api/v1/grid";
#    url = f"https://atlas-api.2.rahtiapp.fi/api/v1/grid/birdAssociation/ML.1091";

    data_dict = common_helpers.fetch_api(url)
#    print(data_dict)

    squares = dict()
    count_squares_reached = 0

    for square in data_dict["gridSquares"]:
        square_id = square["coordinates"]
    
        # Special case for showing target points on the map
        if "tyydyttävä-selvitysaste" == target_class_name:
            until_level = square["level3"]
        # Points needed until defined level
        else:
            until_level = square[target_class_key] - square["atlasClassSum"]
            # If has already passed the level
            if until_level <= 0:
                until_level = 0
                count_squares_reached += 1

        squares[square_id] = dict()
        squares[square_id]["until_level"] = round(until_level, 1)
        squares[square_id]["atlas_class_sum"] = square["atlasClassSum"]
        squares[square_id]["atlas_class_name"] = target_class_name
        
#    print(squares)
    return squares, count_squares_reached


def main(class_untrusted):
    html = dict()

    allowed_classes = {
        "tyydyttävä-selvitysaste": 0,
        "satunnaishavaintoja": 1,
        "välttävä": 2,
        "tyydyttävä": 3,
        "hyvä": 4,
        "erinomainen": 5
    }
    if class_untrusted not in allowed_classes:
        common_helpers.print_log("ERROR: Invalid class name")
        raise ValueError
    else:
        target_class_name = class_untrusted
        target_class_value = allowed_classes[class_untrusted]


    square_data, count_squares_reached = fetch_breeding_sums(target_class_name, target_class_value)

    total_square_count = 3859

    proportion_squares_reached = round((count_squares_reached / total_square_count * 100), 1)

    html["coordinates"] = common_helpers.squares_with_data(square_data, color_viridis_capped, text_summap)
    html["proportion_squares_reached"] = proportion_squares_reached
    html["count_squares_reached"] = count_squares_reached
    html["target_class_name"] = target_class_name

    return html
