
import atlas.common as common

def observation_coordinates(square_id):
    url = f"https://api.laji.fi/v0/warehouse/query/unit/list?selected=gathering.conversions.wgs84CenterPoint.lat%2Cgathering.conversions.wgs84CenterPoint.lon%2Cgathering.coordinatesVerbatim&pageSize=1000&page=1&cache=false&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&time=2022%2F2025&individualCountMin=1&coordinates={square_id}%3AYKJ&qualityIssues=NO_ISSUES&atlasClass=MY.atlasClassEnumA%2CMY.atlasClassEnumB%2CMY.atlasClassEnumC%2CMY.atlasClassEnumD&coordinateAccuracyMax=1000&access_token=";

    data_dict = common.fetch_finbif_api(url, True)

    coord_string = ""
    for obs in data_dict["results"]:
        # Todo: skip those with just center coordinates
        #    if (isset($obs['gathering']['coordinatesVerbatim'])) {
        lat = obs['gathering']['conversions']['wgs84CenterPoint']['lat']
        lon = obs['gathering']['conversions']['wgs84CenterPoint']['lon']
        coord_string = coord_string + f"[{lat},{lon}],\n"

    return coord_string


def main(square_id_untrusted):
    square_id = common.valid_square_id(square_id_untrusted)

    coordinates = observation_coordinates(square_id)

    html = dict()
    html["heading"] = f"Hoi! {square_id}"
    html["coordinates"] = coordinates

    return html
