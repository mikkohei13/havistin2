
import atlas.common_atlas as common_atlas
from helpers import common_helpers

import matplotlib.cm as cm
import numpy as np


def color_viridis_capped(value):
    value = value["list_count"]
    cap = 100

    # Cap value
    if value > cap:
        value = cap
    
    # Normalize value to range [0, 1]
    normalized_value = value / cap

    # Get RGB color value along viridis color scale
    #  viridis, inferno, plasma, magma, jet (spectrum), cool, hot
    # Suffix "_r" reverts the scale
    color = cm.viridis_r(normalized_value)

    r, g, b = tuple(np.array(color[:3]) * 255)
    color = f"rgba({round(r,0)}, {round(g,0)}, {round(b,0)}, 0.9)"

    return color


def text_completelists(value, square_id, square_data):
    if 1 == value["list_count"]:
        text = f"{square_id} {square_data['kunta']}, {square_data['nimi']}:<br>yksi täydellinen lista:<br>{ value['text'] }"
    else:
        text = f"{square_id} {square_data['kunta']}, {square_data['nimi']}:<br>{ value['list_count'] } täydellistä listaa:<br>{ value['text'] }"
    return text


def fetch_completelists_per_square():

    per_page = 10000
    # This sorts the document based on gathering count DESC, i.e. how many units have coordinates.
    url = f"https://api.laji.fi/v0/warehouse/query/gathering/aggregate?aggregateBy=document.documentId%2Cgathering.conversions.ykj10kmCenter.lat%2Cgathering.conversions.ykj10kmCenter.lon&onlyCount=true&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize={ per_page }&page=1&cache=false&qualityIssues=NO_ISSUES&completeListTaxonId=MX.37580&countryId=ML.206&completeListType=MY.completeListTypeCompleteWithBreedingStatus%2CMY.completeListTypeComplete&access_token=";

    data_dict = common_helpers.fetch_finbif_api(url)

    document_ids = dict()
    squares = dict()

    total_list_count = 0

    for list in data_dict["results"]:
        n = list["aggregateBy"]["gathering.conversions.ykj10kmCenter.lat"].split(".")[0]
        e = list["aggregateBy"]["gathering.conversions.ykj10kmCenter.lon"].split(".")[0]
        square_id = n + ":" + e

#        print(square_id)

        document_id = list["aggregateBy"]["document.documentId"]

        # Skip duplicates, i.e. documents that span multiple squares
        if document_id in document_ids:
#            print("Skipping duplicate document_id", document_id)
            continue
        else:
            document_ids[document_id] = True

        # Skip documents without coordinates, what are these?
        if len(square_id) != 7:
#            print("Skipping document without coordinates: ", document_id)
            continue

        total_list_count += 1

        if square_id in squares:
            squares[square_id]["list_count"] += 1
            squares[square_id]["text"] += f"<a href=\\'{ document_id }\\' target=\\'_blank\\'>{ document_id }</a> "
        else:
            squares[square_id] = dict()
            squares[square_id]["list_count"] = 1
            squares[square_id]["text"] = f"<a href=\\'{ document_id }\\' target=\\'_blank\\'>{ document_id }</a> "

#    print(squares)

    return squares, total_list_count


def main():
    html = dict()

    square_data, total_list_count = fetch_completelists_per_square()

    total_square_count = 3859
    
    square_count = len(square_data)
    square_proportion = round((square_count / total_square_count * 100), 1)

    html["stats"] = f"{ total_list_count } täydellistä listaa { square_count } ruudusta, eli { square_proportion } % kaikista ruuduista. Mukana ovat myös listat, jotka ylittävät atlasruudun rajan. Ne tilastoidaan havaintoalueen keskipisteen mukaan."

    html["coordinates"] = common_helpers.squares_with_data(square_data, color_viridis_capped, text_completelists)

    return html
