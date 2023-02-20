
import json
import random
import atlas.common_atlas as common_atlas
from helpers import common_helpers


# Example color function. Takes three arguments: value, square_id and square information dictionary.
def text_example(value, square_id, square_data):
    text = f"{square_id} {square_data['kunta']} {square_data['nimi']}: {value}"
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

    coordinates = ""
    for square_id, value in square_data.items():

        color = colorfunction(value)
        text = textfunction(value, square_id, squares[square_id])

        coordinates = coordinates + f"{{ coords: [[{squares[square_id]['sw-n']},{squares[square_id]['sw-e']}], [{squares[square_id]['nw-n']},{squares[square_id]['nw-e']}], [{squares[square_id]['ne-n']},{squares[square_id]['ne-e']}], [{squares[square_id]['se-n']},{squares[square_id]['se-e']}]], color: '{color}', text: '{text}' }},\n"
    
    return coordinates



def all_squares():
    with open("data/atlas-grids.json") as f:
        squares = json.load(f)

    coordinates = ""
    limit = 4000
    i = 0
    for square_id, d in squares.items():
        text = f"{square_id} {d['kunta']}, {d['nimi']}"

        color = color_random(1)

        coordinates = coordinates + f"{{ coords: [[{d['sw-n']},{d['sw-e']}], [{d['nw-n']},{d['nw-e']}], [{d['ne-n']},{d['ne-e']}], [{d['se-n']},{d['se-e']}]], color: '{color}', text: '{text}' }},\n"
        i = i + 1
        if i >= limit:
            break

    return coordinates


def main(square_id_untrusted):
    html = dict()

    square_data = { "668:338": 10, "667:337": 20, "666:333": 30 }

    html["coordinates"] = all_squares()
#    html["coordinates"] = squares_with_data(square_data, color_example, text_example)

    return html
