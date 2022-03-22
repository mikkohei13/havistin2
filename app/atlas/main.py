
import requests

import json
import sys

import app_secrets

def print_r(dict):
    print("DICT:", file = sys.stdout)
    print(*dict.items(), sep="\n", file = sys.stdout)

def print_debug(data):
    print("DEBUG:", file = sys.stdout)
    print(str(data), file = sys.stdout)

def main(text):
    data = get_collections()
    return data + text + "!"

def get_collections():
    api_url = "https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=document.collectionId&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=100&page=1&cache=true&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&yearMonth=2022%2F2025&individualCountMin=1&qualityIssues=NO_ISSUES&atlasClass=MY.atlasClassEnumB%2CMY.atlasClassEnumC%2CMY.atlasClassEnumD&access_token=" + app_secrets.finbif_api_token

    r = requests.get(api_url)
    dataJson = r.text
    dataDict = json.loads(dataJson)

    print_debug(type(dataDict))
    print_r(dataDict)

    total_obs_count = 0
    for i in dataDict["results"]:
        total_obs_count = total_obs_count + i["count"]

    html_table = "<table>"
    for i in dataDict["results"]:
        print_debug(i)

        html_table += "<tr><td>" + i["aggregateBy"]["document.collectionId"] + "</td>"
        html_table += "<td>" + str(i["count"]) + "</td>"
        html_table += "<td>" + str((i["count"] / total_obs_count) * 100) + " %</td></tr>"
#        print(dataDict["results"]["aggregateBy"]["count"], file = sys.stdout)

    html_table += "</table>"

    return html_table

