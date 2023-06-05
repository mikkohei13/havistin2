
from dataclasses import replace
#import json
import atlas.common_atlas as common_atlas
from helpers import common_helpers


def observation_coordinates(square_id):
    url = f"https://api.laji.fi/v0/warehouse/query/unit/list?selected=gathering.conversions.wgs84CenterPoint.lat%2Cgathering.conversions.wgs84CenterPoint.lon%2Cgathering.coordinatesVerbatim&pageSize=10000&page=1&cache=false&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&time=2022%2F2025&individualCountMin=1&coordinates={square_id}%3AYKJ&qualityIssues=NO_ISSUES&atlasClass=MY.atlasClassEnumB%2CMY.atlasClassEnumC%2CMY.atlasClassEnumD&coordinateAccuracyMax=5000&access_token=";

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
    html = html + "yli 10000 m: <strong>" + str(over10000) + "</strong>, "
    html = html + "5000 m: <strong>" + str(under10000) + "</strong>, "
    html = html + "1000 m: <strong>" + str(under1000) + "</strong>, "
    html = html + "100 m: <strong>" + str(under100) + "</strong>, "
    html = html + "alle 10 m: <strong>" + str(under10) + "</strong>, "

    return html[0:-2]


def observers(square_id):
    url = f"https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=gathering.team.memberName&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=30&page=1&cache=false&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&yearMonth=2022%2F2025&individualCountMin=1&qualityIssues=NO_ISSUES&atlasClass=MY.atlasClassEnumB%2CMY.atlasClassEnumC%2CMY.atlasClassEnumD&coordinates={square_id}%3AYKJ&access_token="

    data = common_helpers.fetch_finbif_api(url)

    html = ""
    html += "<table class='styled-table'>"
    html += "<thead><tr><th>Havainnoija</th><th>Havaintoja</th></tr></thead>"
    html += "<tbody>"

    for item in data["results"]:
        aggregate_by = item["aggregateBy"]["gathering.team.memberName"]
        count = str(item["count"])
        html += "<tr><td>" + aggregate_by + "</td>"
        html += "<td>" + count + "</td>"

    html += "</tbody></table>"
    return html


def main(square_id_untrusted):
    html = dict()

    square_id = common_atlas.valid_square_id(square_id_untrusted)
    html["square_id"] = square_id

    neighbour_ids = common_atlas.neighbour_ids(square_id)
    html["neighbour_ids"] = neighbour_ids

    coordinates, mappable_obs_count = observation_coordinates(square_id)
    html["coordinates"] = coordinates
    html["mappable_obs_count"] = mappable_obs_count

    coordinate_accuracy_data, total_obs_count = common_atlas.coordinate_accuracy_data(square_id)
    html["accuracies"] = coordinate_accuracy_html(coordinate_accuracy_data)

    html["observers"] = observers(square_id)

#    html["total_obs_count"] = collection_counts(square_id)

    square_name, society, centerpoint, cornerpoints = common_atlas.square_info(square_id)
    # Todo: Make heading the same way as on squareform
    html["heading"] = f"{square_id} {square_name}"
    html["centerpoint"] = centerpoint
    html["cornerpoints"] = cornerpoints



    return html
