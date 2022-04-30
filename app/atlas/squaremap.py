
from dataclasses import replace
import atlas.common as common
import json

def observation_coordinates(square_id):
    url = f"https://api.laji.fi/v0/warehouse/query/unit/list?selected=gathering.conversions.wgs84CenterPoint.lat%2Cgathering.conversions.wgs84CenterPoint.lon%2Cgathering.coordinatesVerbatim&pageSize=1000&page=1&cache=false&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&time=2022%2F2025&individualCountMin=1&coordinates={square_id}%3AYKJ&qualityIssues=NO_ISSUES&atlasClass=MY.atlasClassEnumA%2CMY.atlasClassEnumB%2CMY.atlasClassEnumC%2CMY.atlasClassEnumD&coordinateAccuracyMax=1000&access_token=";

    data_dict = common.fetch_finbif_api(url, False)

    coord_string = ""
    for obs in data_dict["results"]:
        # Todo: skip those with just center coordinates
        #    if (isset($obs['gathering']['coordinatesVerbatim'])) {
        lat = obs['gathering']['conversions']['wgs84CenterPoint']['lat']
        lon = obs['gathering']['conversions']['wgs84CenterPoint']['lon']
        coord_string = coord_string + f"[{lat},{lon}],\n"

    return coord_string


# This fixes data that's in string format in the json file
def str2decimal(str):
    str = str.replace(",", ".")
    return str


def square_info(square_id):
    with open("data/atlas-grids.json") as f:
        data = json.load(f)

    # Todo: streamline, use file per square?
    d = data[square_id]

    square_name = d["kunta"] + ", " + d["nimi"]

    centerpoint = str2decimal(d["c-n"]) + "," + str2decimal(d["c-e"])

    cornerpoints = "[" + str(d["sw-n"]) + "," + str(d["sw-e"]) + "], [" + str(d["nw-n"]) + "," + str(d["nw-e"]) + "], [" + str(d["ne-n"]) + "," + str(d["ne-e"]) + "], [" + str(d["se-n"]) + "," + str(d["se-e"]) + "], [" + str(d["sw-n"]) + "," + str(d["sw-e"]) + "]"

    return square_name, centerpoint, cornerpoints

    # read 
# $gCenter = commaToPoint($g['c-n']) . ", " . commaToPoint($g['c-e']);
# $thisGridPoly = "[ [" . $g['sw-n'] . "," . $g['sw-e'] . "], [" . $g['nw-n'] . "," . $g['nw-e'] . "], [" . $g['ne-n'] . "," . $g['ne-e'] . "], [" . $g['se-n'] . "," . $g['se-e'] . "], [" . $g['sw-n'] . "," . $g['sw-e'] . "] ]";


def main(square_id_untrusted):
    square_id = common.valid_square_id(square_id_untrusted)

    coordinates = observation_coordinates(square_id)
    square_name, centerpoint, cornerpoints = square_info(square_id)

    html = dict()

    html["square_id"] = square_id

    # Todo: Make heading the same way as on squareform
    html["heading"] = f"{square_id} {square_name}"

    html["coordinates"] = coordinates
    html["centerpoint"] = centerpoint
    html["cornerpoints"] = cornerpoints

    return html
