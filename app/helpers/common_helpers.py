import requests
import json
import sys

import app_secrets

def print_foo():
    print("FOOOOOOO!")


def print_log(dict):
    print(dict, sep="\n", file = sys.stdout)


def cc_link_html(link, name):
    return f"<a href='{link}'>{name}</a>"


# TODO: make full list of possible licenses
# TODO: make license link
def cc_abbreviation(lic):

    if "http://tun.fi/MZ.intellectualRightsCC-BY-NC-4.0" == lic or "CC-BY-NC-4.0" == lic or "CC BY-NC 4.0" == lic:
        return cc_link_html("https://creativecommons.org/licenses/by-nc/4.0/", "CC BY-NC 4.0")

    if "http://tun.fi/MZ.intellectualRightsCC-BY-SA-4.0" == lic or "CC-BY-SA-4.0" == lic:
        return cc_link_html("https://creativecommons.org/licenses/by-sa/4.0/", "CC BY-SA 4.0")

    if "http://tun.fi/MZ.intellectualRightsCC-BY-4.0" == lic or "CC-BY-4.0" == lic:
        return cc_link_html("https://creativecommons.org/licenses/by/4.0/", "CC BY 4.0")

    if "http://tun.fi/MZ.intellectualRightsCC-BY-NC-ND-4.0" == lic or "CC-BY-NC-ND-4.0" == lic:
        return cc_link_html("https://creativecommons.org/licenses/by-nc-nd/4.0/", "CC BY-NC 4.0")

    if "http://tun.fi/MZ.intellectualRightsCC-BY-NC-SA-4.0" == lic or "CC-BY-NC-SA-4.0" == lic:
        return cc_link_html("https://creativecommons.org/licenses/by-nc-sa/4.0/", "CC BY-NC 4.0")

    if "CC0-4.0" == lic:
        return cc_link_html("https://creativecommons.org/share-your-work/public-domain/cc0/", "CC Zero 4.0")

    if "pd" == lic:
        return "Public Domain"

    if "http://tun.fi/MZ.intellectualRightsARR" == lic:
        return "Kaikki oikeudet pidätetään"

#    if "" == lic or "" == lic:
#        return ""
    return lic


def fetch_finbif_api(api_url, log = False):
    if "&access_token=" not in api_url:
        print("DEV WARNING: access_token param is missing from your url!", file = sys.stdout)

    api_url = api_url + app_secrets.finbif_api_token
    print("Fetching API: " + api_url, file = sys.stdout)

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


def fetch_api(api_url, log = False):
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


# Expects data as:
# { "668:338": 0, "669:338": 10, "670:338": 20  }
def squares_with_data(square_data, colorfunction, textfunction):
    with open("data/atlas-grids.json") as f:
        squares = json.load(f)

    coordinates = ""
    for square_id, value in square_data.items():

        color = colorfunction(value)
        text = textfunction(value, square_id, squares[square_id])

        coordinates = coordinates + f"{{ coords: [[{squares[square_id]['sw-n']},{squares[square_id]['sw-e']}], [{squares[square_id]['nw-n']},{squares[square_id]['nw-e']}], [{squares[square_id]['ne-n']},{squares[square_id]['ne-e']}], [{squares[square_id]['se-n']},{squares[square_id]['se-e']}]], color: '{color}', text: '{text}' }},\n"
    
    return coordinates
