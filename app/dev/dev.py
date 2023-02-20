
import json
import atlas.common_atlas as common_atlas
from helpers import common_helpers


def square_info():
    with open("data/atlas-grids-small.json") as f:
        data = json.load(f)

    coordinates = ""
    limit = 10000
    i = 0
    for square_id, d in data.items():
        coordinates = coordinates + f"[[{d['sw-n']},{d['sw-e']}], [{d['nw-n']},{d['nw-e']}], [{d['ne-n']},{d['ne-e']}], [{d['se-n']},{d['se-e']}], [{d['sw-n']},{d['sw-e']}]],\n"
        i = i + 1
        if i >= limit:
            break

    return coordinates


def main(square_id_untrusted):
    html = dict()

    html["coordinates"] = square_info()

    return html
