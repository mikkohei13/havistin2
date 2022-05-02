
from dataclasses import replace
import atlas.common as common
import json


def observation_coordinates(square_id):
    url = f"https://api.laji.fi/v0/warehouse/query/unit/list?selected=gathering.conversions.wgs84CenterPoint.lat%2Cgathering.conversions.wgs84CenterPoint.lon%2Cgathering.coordinatesVerbatim&pageSize=1000&page=1&cache=true&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&time=2022%2F2025&individualCountMin=1&coordinates={square_id}%3AYKJ&qualityIssues=NO_ISSUES&atlasClass=MY.atlasClassEnumB%2CMY.atlasClassEnumC%2CMY.atlasClassEnumD&coordinateAccuracyMax=1000&access_token=";

    data_dict = common.fetch_finbif_api(url, True)

    obs_count = data_dict["total"] 

    coord_string = ""
    for obs in data_dict["results"]:
        # Todo: skip those with just center coordinates
        #    if (isset($obs['gathering']['coordinatesVerbatim'])) {
        lat = obs['gathering']['conversions']['wgs84CenterPoint']['lat']
        lon = obs['gathering']['conversions']['wgs84CenterPoint']['lon']
        coord_string = coord_string + f"[{lat},{lon}],\n"

    return coord_string, obs_count


# This fixes data that's in string format in the json file
def str2decimal(str):
    str = str.replace(",", ".")
    return str


def square_info(square_id):
    with open("data/atlas-grids.json") as f:
        data = json.load(f)

    # Todo: streamline, use file per square?
    # Todo: validate that square exists. Test case: 677:377
    d = data[square_id]

    square_name = d["kunta"] + ", " + d["nimi"]

    centerpoint = str2decimal(d["c-n"]) + "," + str2decimal(d["c-e"])

    cornerpoints = "[" + str(d["sw-n"]) + "," + str(d["sw-e"]) + "], [" + str(d["nw-n"]) + "," + str(d["nw-e"]) + "], [" + str(d["ne-n"]) + "," + str(d["ne-e"]) + "], [" + str(d["se-n"]) + "," + str(d["se-e"]) + "], [" + str(d["sw-n"]) + "," + str(d["sw-e"]) + "]"

    return square_name, centerpoint, cornerpoints

    # read 
# $gCenter = commaToPoint($g['c-n']) . ", " . commaToPoint($g['c-e']);
# $thisGridPoly = "[ [" . $g['sw-n'] . "," . $g['sw-e'] . "], [" . $g['nw-n'] . "," . $g['nw-e'] . "], [" . $g['ne-n'] . "," . $g['ne-e'] . "], [" . $g['se-n'] . "," . $g['se-e'] . "], [" . $g['sw-n'] . "," . $g['sw-e'] . "] ]";

def coordinate_accuracy_html_loop(data):
    html = ""
    for accuracy, count in data.items():
        html = html + accuracy + " m: " + str(count) +  " havaintoa, "

    return html[0:-2]


def coordinate_accuracy_html(data):

    over10000 = data.get("over", 0) + data.get("25000", 0) + data.get("10000", 0)
    under10000 =data.get("5000", 0)
    under1000 =data.get("1000", 0)
    under100 = data.get("100", 0)
    under10 = data.get("10", 0) + data.get("1", 0)

    mappable = under10000 + under1000 + under100 + under10
    total = over10000 + mappable

    if 0 == total:
        return "Ruutulta ei ole vielä havaintoja"

    mappable_percentage = round(mappable / total * 100, 1)

    html = f"Kartalla näytetään <strong>{mappable_percentage} %</strong> ruudun <strong>{total} havainnosta</strong>. Havaintojen määrä eri tarkkuusluokissa: "
    html = html + "yli 10000 m: " + str(over10000) + ", "
    html = html + "5000 m: " + str(under10000) + ", "
    html = html + "1000 m: " + str(under1000) + ", "
    html = html + "100 m: " + str(under100) + ", "
    html = html + "alle 10 m: " + str(under10) + ", "

    return html[0:-2]


def main(square_id_untrusted):
    html = dict()

    square_id = common.valid_square_id(square_id_untrusted)
    html["square_id"] = square_id

    neighbour_ids = common.neighbour_ids(square_id)
    html["neighbour_ids"] = neighbour_ids

    coordinates, mappable_obs_count = observation_coordinates(square_id)
    html["coordinates"] = coordinates
    html["mappable_obs_count"] = mappable_obs_count

    coordinate_accuracy_data, total_obs_count = common.coordinate_accuracy_data(square_id)
    html["accuracies"] = coordinate_accuracy_html(coordinate_accuracy_data)

#    html["total_obs_count"] = collection_counts(square_id)

    square_name, centerpoint, cornerpoints = square_info(square_id)
    # Todo: Make heading the same way as on squareform
    html["heading"] = f"{square_id} {square_name}"
    html["centerpoint"] = centerpoint
    html["cornerpoints"] = cornerpoints



    return html
