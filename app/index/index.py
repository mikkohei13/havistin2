
import requests
import json
import sys

import app_secrets
from helpers import common_helpers

def check_api():

    # Check by fetching 10 latest observations from today
    api_url = "https://api.laji.fi/v0/warehouse/query/list?countryId=ML.206&time=0/0&aggregateBy=unit.interpretations.recordQuality,document.linkings.collectionQuality,unit.linkings.taxon.taxonomicOrder,unit,unit.abundanceString,gathering.displayDateTime,gathering.interpretations.countryDisplayname,gathering.interpretations.biogeographicalProvinceDisplayname,gathering.locality,document.collectionId,document.documentId,gathering.team,document.secureLevel,unit.unitId,document.documentId&selected=unit.interpretations.recordQuality,document.linkings.collectionQuality,unit.linkings.taxon.taxonomicOrder,unit,unit.abundanceString,gathering.displayDateTime,gathering.interpretations.countryDisplayname,gathering.interpretations.biogeographicalProvinceDisplayname,gathering.locality,document.collectionId,document.documentId,gathering.team,document.secureLevel,unit.unitId,document.documentId&cache=true&page=1&pageSize=10&access_token="
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

    # Todo: how these are logged? On Google Cloud docs?

#    print(dataDict, file = sys.stdout)
    return dataDict


def main():
    html = dict()

    common_helpers.print_foo()

    api_up = check_api()

    # This is special for front page: check that API is up and give error for user if not.
    html["error"] = ""
    if api_up == False:
        html["error"] = "<p id='apierror'>Lajitietokeskuksen rajapinta ei juuri nyt toimi. Ole hyvä ja yritä myöhemmin uudelleen!</p>"
        return html

    # API works, proceed normally
    html["today_obs_count"] = api_up["total"]


    return html