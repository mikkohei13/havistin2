
from dataclasses import replace
#import json
import atlas.common_atlas as common_atlas
from helpers import common_helpers


def observation_coordinates(square_id):
    url = f"https://api.laji.fi/v0/warehouse/query/unit/list?selected=gathering.conversions.wgs84CenterPoint.lat%2Cgathering.conversions.wgs84CenterPoint.lon%2Cgathering.coordinatesVerbatim&pageSize=1000&page=1&cache=false&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&time=2022%2F2025&individualCountMin=1&coordinates={square_id}%3AYKJ&qualityIssues=NO_ISSUES&atlasClass=MY.atlasClassEnumB%2CMY.atlasClassEnumC%2CMY.atlasClassEnumD&coordinateAccuracyMax=5000&access_token=";

    data_dict = common_helpers.fetch_finbif_api(url)

    obs_count = data_dict["total"] 

    coord_string = ""
    for obs in data_dict["results"]:
        # Todo: skip those with just center coordinates
        #    if (isset($obs['gathering']['coordinatesVerbatim'])) {
        lat = obs['gathering']['conversions']['wgs84CenterPoint']['lat']
        lon = obs['gathering']['conversions']['wgs84CenterPoint']['lon']
        coord_string = coord_string + f"[{lat},{lon}],\n"

    return coord_string, obs_count


def coordinate_accuracy_html_loop(data):
    html = ""
    for accuracy, count in data.items():
        html = html + accuracy + " m: " + str(count) +  " havaintoa, "

    return html[0:-2]





def main(square_id_untrusted):
    html = dict()

    square_id = common_atlas.valid_square_id(square_id_untrusted)
    html["square_id"] = square_id

    coordinate_accuracy_data, total_obs_count = common_atlas.coordinate_accuracy_data(square_id)

    square_name, society, centerpoint, cornerpoints = common_atlas.square_info(square_id)

    html["heading"] = f"{square_id} {square_name}"
    html["centerpoint"] = centerpoint
    html["cornerpoints"] = cornerpoints



    return html
