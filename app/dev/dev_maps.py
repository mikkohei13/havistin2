
import json
import random
import atlas.common_atlas as common_atlas
from helpers import common_helpers

import matplotlib.cm as cm
import numpy as np


def color_viridis(value):
    # Normalize value to range [0, 1]
    normalized_value = value / 100

    # Get RGB color value along viridis color scale
    #  viridis, inferno, plasma, magma, jet (spectrum), cool, hot
    # Suffix "_r" reverts the scale
    color = cm.viridis_r(normalized_value)

    r, g, b = tuple(np.array(color[:3]) * 255)
    color = f"rgba({round(r,0)}, {round(g,0)}, {round(b,0)}, 0.9)"

    return color


# Example color function. Takes three arguments: value, square_id and square information dictionary.
def text_example(value, square_id, square_data):
    text = f"{common_helpers.escape_html(square_id)} {common_helpers.escape_html(square_data['kunta'])} {common_helpers.escape_html(square_data['nimi'])}: {common_helpers.escape_html(value)}"
    return text


# Example color function. Takes one argument.
def color_example(value):
    b = value * 10
    if b > 255:
        b = 255
    return f"rgba(0, 0, {b}, 0.9)"


def color_random(value_unused):
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return f"rgba({r}, {g}, {b}, 0.9)"


def color_namelength(name):
    name_length = len(name)
    color_length = name_length * 10
    return f"rgba({color_length}, {color_length}, {color_length}, 0.9)"


def squares_with_data(square_data, colorfunction, textfunction):
    with open("data/atlas-grids.json") as f:
        squares = json.load(f)

    polygons = []
    for square_id, value in square_data.items():
        square = squares[square_id]
        polygons.append(common_helpers.square_polygon(
            square,
            colorfunction(value),
            textfunction(value, square_id, square),
        ))

    return polygons


def all_squares():
    with open("data/atlas-grids.json") as f:
        squares = json.load(f)

    polygons = []
    limit = 4000
    i = 0
    for square_id, d in squares.items():
        text = f"{common_helpers.escape_html(square_id)} {common_helpers.escape_html(d['kunta'])}, {common_helpers.escape_html(d['nimi'])}"
        polygons.append(common_helpers.square_polygon(d, color_random(1), text))
        i = i + 1
        if i >= limit:
            break

    return polygons


def main(square_id_untrusted):
    html = dict()

    square_data = { "668:338": 0, "669:338": 10, "670:338": 20, "671:338": 30, "672:338": 40, "673:338": 50, "674:338": 60, "675:338": 70, "676:338": 80, "677:338": 90, "678:338": 100  }

    html["coordinates"] = all_squares()
    html["coordinates"] = squares_with_data(square_data, color_viridis, text_example)

    return html
