
import requests
import json
import sys
from datetime import datetime

import app_secrets
from helpers import common_helpers

def check_api():

    # Check by fetching 10 latest observations from today
    api_url = "https://api.laji.fi/v0/warehouse/query/list?countryId=ML.206&time=0/0&aggregateBy=unit.abundanceString,gathering.displayDateTime,gathering.interpretations.countryDisplayname,gathering.locality,document.collectionId,document.documentId,gathering.team&selected=unit.abundanceString,gathering.displayDateTime,gathering.interpretations.countryDisplayname,gathering.locality,document.collectionId,document.documentId,gathering.team&cache=false&page=1&pageSize=10&access_token="
    api_url += app_secrets.finbif_api_token
    print(api_url)

    try:
        r = requests.get(api_url)
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("Havistin error: HTTPError.", file = sys.stdout)
        return False
    except requests.exceptions.ConnectionError as e:
        print("Havistin error: ConnectionError.", file = sys.stdout)
        return False
    except requests.exceptions.Timeout as e:
        print("Havistin error: Timeout.", file = sys.stdout)
        return False
    except requests.exceptions.TooManyRedirects as e:
        print("Havistin error: TooManyRedirects.", file = sys.stdout)
        return False
    except requests.exceptions.RequestException as e:
        print("Havistin error: RequestException.", file = sys.stdout)
        return False

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

    # Todo: how these (above) are logged? On Google Cloud docs?

    return dataDict

def get_today_saved_total():

    time = datetime.now()
    today = time.strftime("%Y-%m-%d")
    current_year = time.strftime("%Y")

    data = common_helpers.fetch_finbif_api(f"https://api.laji.fi/v0/warehouse/query/unit/aggregate?countryId=ML.206&aggregateBy=document.collectionId&selected=document.collectionId&cache=false&page=1&pageSize=100&firstLoadedSameOrAfter={today}&geoJSON=false&onlyCount=false&access_token=")

    total = 0
    for collection in data["results"]:
        total += collection["count"]
    
    return total, today, current_year


def main():
    html = dict()

    api_up = check_api()

    # This is special for front page: check that API is up and give error for user if not.
    html["error"] = False
    if api_up == False:
        common_helpers.print_log("HÄR")
        html["error"] = True
        return html

    # API works, proceed normally
    html["today_obs_count"] = api_up["total"]

    html["today_saved_count"], html["today"], html['current_year'] = get_today_saved_total()

    return html