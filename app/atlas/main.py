
import requests
from datetime import timedelta, date
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

#    print_debug(type(dataDict))
#    print_r(dataDict)

    total_obs_count = 0
    for i in dataDict["results"]:
        total_obs_count = total_obs_count + i["count"]

    collections_table = "<h3>Havaintolähteet</h3>"
    collections_table += "<table class='styled-table'>"
    collections_table += "<thead><tr><th>Järjestelmä</th><th>Havaintoja</th><th>%</th></tr></thead>"
    collections_table += "<tbody>"

    for i in dataDict["results"]:
        print_debug(i)

        collections_table += "<tr><td>" + get_collection_name(i["aggregateBy"]["document.collectionId"]) + "</td>"
        collections_table += "<td>" + str(i["count"]) + "</td>"
        collections_table += "<td>" + str(round((i["count"] / total_obs_count) * 100, 1)) + " %</td></tr>"
#        print(dataDict["results"]["aggregateBy"]["count"], file = sys.stdout)

    collections_table += "</tbody></table>"

    return collections_table


def daterange(start_date):
    end_date = date.today()

    # inclusive end
    day_count = int((end_date - start_date).days) + 1

    for n in range(day_count):
        yield start_date + timedelta(n)




def datechart_data():

    # Get daily data from api. This lacks dates with zero count.
    api_url ="https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=document.firstLoadDate&orderBy=document.firstLoadDate&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=365&page=1&cache=true&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&yearMonth=2022%2F2025&individualCountMin=1&qualityIssues=NO_ISSUES&atlasClass=MY.atlasClassEnumB%2CMY.atlasClassEnumC%2CMY.atlasClassEnumD&access_token=" + app_secrets.finbif_api_token

    r = requests.get(api_url)
    dataJson = r.text
    dataDict = json.loads(dataJson)

#    print_debug(type(dataDict))
#    print_r(dataDict)

    # Use day as key in dict
    data_by_days = dict()
    for item in dataDict["results"]:
        data_by_days[item["aggregateBy"]["document.firstLoadDate"]] = item["count"]

    # Loop all dates so far, to generate chart.js data list.
    start_date = date(2022, 2, 1)

    cumulative_count = 0
    chartsj_data = []

    for single_date in daterange(start_date):

        if single_date.strftime("%Y-%m-%d") in data_by_days:
            count = data_by_days[single_date.strftime("%Y-%m-%d")]
        else:
            count = 0

        cumulative_count = cumulative_count + count

        # JSON
        daily = dict(x = single_date.strftime("%Y-%m-%d"), y = str(cumulative_count))
        chartsj_data.append(daily)

    json_data = json.dumps(chartsj_data)

    return json_data


def main():
    html = dict()

    html["collections_table"] = get_collections()
    html["datechart_data"] = datechart_data()

    return html
