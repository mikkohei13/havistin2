import requests
import json
import sys
import re

import app_secrets

def print_log(dict):
    print(dict, sep="\n", file = sys.stdout)


def neighbour_ids(square_id):
    links = dict()
    latlon = square_id.split(":")
    links["n"] = str(int(latlon[0]) + 1) + ":" + latlon[1]
    links["e"] = latlon[0] + ":" + str(int(latlon[1]) + 1)
    links["s"] = str(int(latlon[0]) -1) + ":" + latlon[1]
    links["w"] = latlon[0] + ":" + str(int(latlon[1]) - 1)

    return links

def valid_square_id(square_id):
    pattern = r'[6-7][0-9][0-9]:[3-3][0-7][0-9]'
    match = re.fullmatch(pattern, square_id)

    if match is not None:
        return square_id
    else:
        print_log("ERROR: Coordinates invalid: " + square_id)
        raise ValueError


def fetch_finbif_api(api_url, log = False):
    api_url = api_url + app_secrets.finbif_api_token
#    print(api_url, file = sys.stdout)

    if log:
        print_log(api_url)

    try:
        r = requests.get(api_url)
    except ConnectionError:
        print("ERROR: api.laji.fi complete error.", file = sys.stdout)

#    r.encoding = encoding
    dataJson = r.text
    dataDict = json.loads(dataJson)

    if "status" in dataDict:
        if 403 == dataDict["status"]:
            print("ERROR: api.laji.fi 403 error.", file = sys.stdout)
            raise ConnectionError

#    print(dataDict, file = sys.stdout)
    return dataDict


def coordinate_accuracy_data(square_id = False):
    if square_id:
        coordinates = f"&coordinates={square_id}%3AYKJ"
    else:
        coordinates = ""
    
    api_url = f"https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=gathering.interpretations.coordinateAccuracy{coordinates}&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=100&page=1&cache=false&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&yearMonth=2022%2F2025&individualCountMin=1&qualityIssues=NO_ISSUES&atlasClass=MY.atlasClassEnumB%2CMY.atlasClassEnumC%2CMY.atlasClassEnumD&access_token="

    data_dict = fetch_finbif_api(api_url, False)

    accuracy_dict = dict()
    total_count = 0
    for item in data_dict["results"]:
        accuracy_text = ""        
        accuracy = int(item["aggregateBy"]["gathering.interpretations.coordinateAccuracy"])
        count = item["count"]
        total_count = total_count + count

        if accuracy == 1:
            accuracy_text = "1"
        elif accuracy <= 10:
            accuracy_text = "10"
        elif accuracy <= 100:
            accuracy_text = "100"
        elif accuracy <= 1000:
            accuracy_text = "1000"
        elif accuracy <= 5000:
            accuracy_text = "5000"
        elif accuracy <= 10000:
            accuracy_text = "10000"
        elif accuracy <= 25000:
            accuracy_text = "25000"
        else:
            accuracy_text = "over"

        # Todo: better way to do this?    
        if accuracy_text in accuracy_dict:
            accuracy_dict[accuracy_text] = accuracy_dict[accuracy_text] + count
        else:
            accuracy_dict[accuracy_text] = count

    return accuracy_dict, total_count
