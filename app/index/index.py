
import requests
import json
import sys

import app_secrets

def check_api():

    api_url = "https://apiX.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=document.collectionId&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=1&page=1&cache=true&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&individualCountMin=1&access_token="
    api_url += app_secrets.finbif_api_token
    print(api_url)

    try:
        r = requests.get(api_url)
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("Havistin error: HTTPError.", file = sys.stdout)
        return False
#    except requests.exceptions.ConnectionError as e:
#        print("Havistin error: ConnectionError.", file = sys.stdout)
#        return False
    except requests.exceptions.Timeout as e:
        print("Havistin error: Timeout.", file = sys.stdout)
        return False
    except requests.exceptions.TooManyRedirects as e:
        print("Havistin error: TooManyRedirects.", file = sys.stdout)
        return False
#    except requests.exceptions.RequestException as e:
#        print("Havistin error: RequestException.", file = sys.stdout)
#        return False

    dataJson = r.text

    try:
        dataDict = json.loads(dataJson)
    except ValueError as e:
        print("Havistin error: api.laji.fi did not return JSON.", file = sys.stdout)
#        raise Exception("No JSON")
        return False

    if "status" in dataDict:
        if 403 == dataDict["status"]:
            print("Havistin error: api.laji.fi 403 error: " + str(dataDict["message"]), file = sys.stdout)
            return False
        if 400 == dataDict["status"]:
            print("Havistin error: api.laji.fi 404 error: " + str(dataDict["message"]), file = sys.stdout)
            return False

    return True

def main():
    html = dict()

    api_up = check_api()

    if (api_up):
        html["foo"] = "API is up"
        # Give links, show stats
    else:
        html["foo"] = "API is DOWN"
        # Show error, give links



    return html