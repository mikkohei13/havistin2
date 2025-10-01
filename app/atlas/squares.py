
import atlas.common_atlas as common_atlas
from helpers import common_helpers


def square_data(accuracy = 10000):

    api_url = f"https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=gathering.conversions.ykj10km.lat%2Cgathering.conversions.ykj10km.lon&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=30&page=1&cache=true&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&yearMonth=2022%2F2025&individualCountMin=1&coordinateAccuracyMax={accuracy}&qualityIssues=NO_ISSUES&atlasClass=MY.atlasClassEnumB%2CMY.atlasClassEnumC%2CMY.atlasClassEnumD&access_token="

    data_dict = common_helpers.fetch_finbif_api(api_url)

    square_dict = dict()
    for item in data_dict["results"]:
        lat = item["aggregateBy"]["gathering.conversions.ykj10km.lat"][0:3]
        lon = item["aggregateBy"]["gathering.conversions.ykj10km.lon"][0:3]
        square_id = str(lat) + ":" + str(lon)
        square_dict[square_id] = item["count"]

    return square_dict


def square_html(data_dict):

    html = "<table class='styled-table'>"
    html += "<thead><tr><th>Ruutu</th><th>Havaintoja</th></tr></thead>"
    html += "<tbody>"

    for key, value in data_dict.items():
        name = common_atlas.square_name(key) 
        html += "<tr>"
        html += "<td><a href='/atlas/ruutu/" + key + "'>" + key + " " + name + "</a></td>"
        html += "<td>" + str(value) + "</td>"
        html += "</tr>"

    html += "</tbody></table>"
    return html


def main():
    html = dict()

    square_data_dict = square_data()
    html["squares"] = square_html(square_data_dict)

    accurate_square_data_dict = square_data(1000)
    html["accurate_squares"] = square_html(accurate_square_data_dict)

    return html
