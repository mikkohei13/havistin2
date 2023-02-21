
import json
import random
import atlas.common_atlas as common_atlas
from helpers import common_helpers

import matplotlib.cm as cm
import numpy as np


def color_viridis_capped(value):
    # Cap value
    if value > 100:
        value = 100
    
    # Normalize value to range [0, 1]
    normalized_value = value / 100

    # Get RGB color value along viridis color scale
    #  viridis, inferno, plasma, magma, jet (spectrum), cool, hot
    # Suffix "_r" reverts the scale
    color = cm.viridis_r(normalized_value)

    r, g, b = tuple(np.array(color[:3]) * 255)
    color = f"rgba({round(r,0)}, {round(g,0)}, {round(b,0)}, 0.9)"

    return color


def text_completelists(value, square_id, square_data):
    if 1 == value:
        text = f"{square_id} {square_data['kunta']}, {square_data['nimi']}:<br>yksi täydellinen lista"
    else:
        text = f"{square_id} {square_data['kunta']}, {square_data['nimi']}:<br>{value} täydellistä listaa"
    return text


def squares_with_data(square_data, colorfunction, textfunction):
    with open("data/atlas-grids.json") as f:
        squares = json.load(f)

    coordinates = ""
    for square_id, value in square_data.items():

        color = colorfunction(value)
        text = textfunction(value, square_id, squares[square_id])

        coordinates = coordinates + f"{{ coords: [[{squares[square_id]['sw-n']},{squares[square_id]['sw-e']}], [{squares[square_id]['nw-n']},{squares[square_id]['nw-e']}], [{squares[square_id]['ne-n']},{squares[square_id]['ne-e']}], [{squares[square_id]['se-n']},{squares[square_id]['se-e']}]], color: '{color}', text: '{text}' }},\n"
    
    return coordinates


def fetch_completelists_per_square():

    per_page = 4000
    url = f"https://api.laji.fi/v0/warehouse/query/gathering/aggregate?aggregateBy=gathering.conversions.ykj10km.lat%2Cgathering.conversions.ykj10km.lon&onlyCount=true&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize={ per_page }&page=1&cache=false&countryId=ML.206&time=2022%2F2025&qualityIssues=NO_ISSUES&completeListTaxonId=MX.37580&completeListType=MY.completeListTypeCompleteWithBreedingStatus%2CMY.completeListTypeComplete&access_token=";

    data_dict = common_helpers.fetch_finbif_api(url)
    square_data = dict()

    max_list_per_square = 0
    max_list_in_square_id = ""
    squares_with_completelists = 0

    for square in data_dict["results"]:
        squares_with_completelists += 1

        n = square["aggregateBy"]["gathering.conversions.ykj10km.lat"].split(".")[0]
        e = square["aggregateBy"]["gathering.conversions.ykj10km.lon"].split(".")[0]
        count = square["count"]
        square_id = n + ":" + e

        square_data[square_id] = count

        # Update best square
        if count > max_list_per_square:
            max_list_per_square = count
            max_list_in_square_id = square_id

    return square_data, max_list_in_square_id, max_list_per_square, squares_with_completelists




def main():
    html = dict()

    square_data, max_list_in_square_id, max_list_per_square, squares_with_completelists = fetch_completelists_per_square()

#    square_data = { "668:338": 0, "669:338": 10, "670:338": 20, "671:338": 30, "672:338": 40, "673:338": 50, "674:338": 60, "675:338": 70, "676:338": 80, "677:338": 90, "678:338": 100  }

    html["stats"] = f"Täydellisiä listoja { squares_with_completelists } ruudusta, eniten ruudusta { max_list_in_square_id }, josta { max_list_per_square } listaa."
    html["coordinates"] = squares_with_data(square_data, color_viridis_capped, text_completelists)

    return html
