
import json
import random
import atlas.common_atlas as common_atlas
from helpers import common_helpers


def square_info():
    with open("data/atlas-grids.json") as f:
        data = json.load(f)

    coordinates = ""
    limit = 4000
    i = 0
    for square_id, d in data.items():

        # Random square color
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        color = f"rgba({r}, {g}, {b}, 0.9)"

        # Square color based on name length
        '''
        name_length = len( d['nimi'])
        color_length = name_length * 10
        color = f"rgba({color_length}, {color_length}, {color_length}, 0.9)"
        '''
        
        text = f"{square_id} {d['kunta']}, {d['nimi']}"

        coordinates = coordinates + f"{{ coords: [[{d['sw-n']},{d['sw-e']}], [{d['nw-n']},{d['nw-e']}], [{d['ne-n']},{d['ne-e']}], [{d['se-n']},{d['se-e']}]], color: '{color}', text: '{text}' }},\n"
        i = i + 1
        if i >= limit:
            break

    return coordinates


def main(square_id_untrusted):
    html = dict()

    html["coordinates"] = square_info()

    return html
