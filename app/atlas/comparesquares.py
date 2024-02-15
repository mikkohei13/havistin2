# Controller for a page that compares square data between 3rd and 4th data

import re
import pandas as pd
import math

import atlas.common_atlas as common_atlas
from helpers import common_helpers

def get_society_squares(society_id):
    url = f"https://atlas-api.rahtiapp.fi/api/v1/grid/birdAssociation/{ society_id }"
    data = common_helpers.fetch_api(url)
    return data


def validate_society_id(s):
    pattern = r'^[A-Z]{2}\.[0-9]{1,4}$'
    if re.match(pattern, s) and int(s.split('.')[1]) < 10000:
        return s
    else:
        return "ML.1091" # Tringa


def breeding_category_number_to_string(n):
    if n == 0:
        return "Ei havaintoja"
    if n == 1:
        return "Satunnaishavaintoja"
    if n == 2:
        return "Välttävä"
    if n == 3:
        return "Tyydyttävä"
    if n == 4:
        return "Hyvä"
    if n == 5:
        return "Erinomainen"
    return "Ei tiedossa"


def main(society_untrusted):
    html = dict()
    html["heading"] = "Ruutuvertailu"

    society_id = validate_society_id(society_untrusted)
    squares = get_society_squares(society_id)

    html["society_name"] = squares["birdAssociationArea"]["value"]

    table = "<table class='styled-table'><thead><tr><th>YKJ</th><th>Nimi</th><th>3. summa</th><th>3. selvitysaste</th><th>4. summa</th><th>4. selvitysaste</th><th>%</th><th></th></tr></thead>\n<tbody>"

    df = pd.read_csv("./data/atlas3-griddata.csv", delimiter = ";")

    # Loop squares["gridSquares"] and get data for each square
    for square in squares["gridSquares"]:
        coordinates = square["coordinates"]
        name = square["name"]
        sum = square["atlasClassSum"]
        category = square["activityCategory"]["value"]
        category_class = category.replace("ä", "a")

        square_3rd = df[(df["grid"] == coordinates)]

        sum_3rd = square_3rd["activitySum"].values[0]
        category_3rd = breeding_category_number_to_string(square_3rd["activityCategory"].values[0])

        if sum_3rd == 0 or sum == 0:
            proportion = 0
            percentage = 0
            percentage_class = "p_0"
        else:
            proportion = (sum / sum_3rd) * 100
            percentage = int(round(proportion, 0))
            percentage_class = "p_" + str(int(math.floor(proportion / 10)))

        table += f"<tr class='{ percentage_class } { category_class }'><td><a href='/atlas/puutelista/{ coordinates }' title='Puutelista'>{ coordinates }</a></td><td><a href='/atlas/ruutulomake/{ coordinates }/vakio' title='Tulostettava ruutulomake'>{ name }</a></td><td>{ sum_3rd }</td><td>{ category_3rd }</td><td>{ sum }</td><td>{ category }</td><td>{ percentage }&nbsp;%</td><td><span>&nbsp;</span></td></tr>"

    table += "\n</tbody></table>"
    html["table"] = table

    return html


