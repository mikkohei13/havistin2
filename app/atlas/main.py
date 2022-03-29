
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

def get_collection_name(id):
    if "http://tun.fi/HR.4412" == id:
        return "Tiira"
    elif  "http://tun.fi/HR.4471" == id:
        return "Vihko, lintuatlaslomake"
    elif  "http://tun.fi/HR.1747" == id:
        return "Vihko, retkilomake"
    elif  "http://tun.fi/HR.3211" == id:
        return "iNaturalist Suomi"
    else:
        return "Muu"


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

    html_table = "<table class='styled-table'>"
    html_table += "<thead><tr><th>Lähde</th><th>Havaintoja</th><th>%</th></tr></thead>"
    html_table += "<tbody>"

    for i in dataDict["results"]:
        print_debug(i)

        html_table += "<tr><td>" + get_collection_name(i["aggregateBy"]["document.collectionId"]) + "</td>"
        html_table += "<td>" + str(i["count"]) + "</td>"
        html_table += "<td>" + str(round((i["count"] / total_obs_count) * 100, 1)) + " %</td></tr>"
#        print(dataDict["results"]["aggregateBy"]["count"], file = sys.stdout)

    html_table += "</tbody></table>"

    return html_table


def main(text):
    data = get_collections()
    return data
