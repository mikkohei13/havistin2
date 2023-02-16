import time
import os.path

import atlas.common_atlas as common_atlas
from helpers import common_helpers

def observer_name(user_id):
    user_qname = user_id.replace("http://tun.fi/", "")
#    filename = "./cache/" + user_qname + ".txt"

    # Get from cache
#    if os.path.exists(filename):
#        with open(filename) as f:
#            name = f.readlines()
#        return name[0]

    # Get from API, save to cache 
    api_url = f"https://api.laji.fi/v0/person/by-id/{user_qname}?access_token="
    data = common_helpers.fetch_finbif_api(api_url)
    name = data["fullName"]

#    with open(filename, 'w+') as f:
#        f.write(name)
    return name


def complete_lists():
    api_url = "https://api.laji.fi/v0/warehouse/query/document/aggregate?aggregateBy=document.editorUserIds&onlyCount=true&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=30&page=1&cache=true&qualityIssues=NO_ISSUES&completeListTaxonId=MX.37580&completeListType=MY.completeListTypeCompleteWithBreedingStatus%2CMY.completeListTypeComplete&access_token="

    data = common_helpers.fetch_finbif_api(api_url)

    html = ""
    html += "<table class='styled-table'>"
    html += "<thead><tr><th>Havainnoija</th><th>Listoja</th></tr></thead>"
    html += "<tbody>"

    for item in data["results"]:
        # TODO: for some reason, fetching from localhost api is not working well
        # TODO: common function, which caches data locally

        count = str(item["count"])
        name = observer_name(item["aggregateBy"]["document.editorUserIds"])
        html += "<tr><td>" + name + "</td>"
        html += "<td>" + count + "</td>"

    html += "</tbody></table>"
    return html


def recent_observers():
    # observations loaded to FinBIF during last 48 hours, excluding Tiira
    # 48 h: 172800
    timestamp = int(time.time()) -172800

    url = f"https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=gathering.team.memberName&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=20&page=1&cache=true&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&firstLoadedSameOrAfter={timestamp}&yearMonth=2022%2F2025&individualCountMin=1&qualityIssues=NO_ISSUES&atlasClass=MY.atlasClassEnumB%2CMY.atlasClassEnumC%2CMY.atlasClassEnumD&collectionIdNot=HR.4412&access_token="

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


def societies():
    # TODO: All observations per society, requires new api endpoint from laji.fi
    # Tiira observations
    url = "https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=gathering.team.memberName&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=50&page=1&cache=true&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&yearMonth=2022%2F2025&individualCountMin=1&qualityIssues=NO_ISSUES&atlasClass=MY.atlasClassEnumB%2CMY.atlasClassEnumC%2CMY.atlasClassEnumD&collectionId=HR.4412&access_token="

    data = common_helpers.fetch_finbif_api(url)

    html = ""
    html += "<table class='styled-table'>"
    html += "<thead><tr><th>Yhdistys</th><th>Havaintoja</th></tr></thead>"
    html += "<tbody>"

    for item in data["results"]:
        aggregate_by = item["aggregateBy"]["gathering.team.memberName"]
        count = str(item["count"])
        html += "<tr><td>" + aggregate_by + "</td>"
        html += "<td>" + count + "</td>"

    html += "</tbody></table>"
    return html


def main():
    html = dict()

    html["complete_lists"] = complete_lists()

    html["recent_observers"] = recent_observers()

    html["societies"] = societies()

    return html
