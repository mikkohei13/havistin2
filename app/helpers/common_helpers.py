import requests
import json
import sys
import re

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


def fetch_finbif_api(api_url, person_token=None, log=False):
    # API v1: send access token and other params as headers instead of query params
    headers = {
        'Authorization': f'Bearer {app_secrets.finbif_api_token}',
        'API-Version': '1'
    }

    if person_token:
        headers['Person-Token'] = person_token

    # Convert v0 base path to v1
    api_url = api_url.replace('api.laji.fi/v0/', 'api.laji.fi/')

    # Extract lang param and send as Accept-Language header instead
    lang_match = re.search(r'[?&]lang=(fi|en|sv)(?=&|$)', api_url)
    if lang_match:
        headers['Accept-Language'] = lang_match.group(1)
        api_url = re.sub(r'(\?)lang=(fi|en|sv)&', r'\1', api_url)
        api_url = re.sub(r'&lang=(fi|en|sv)(?=&|$)', '', api_url)

    # Remove access_token query param (now sent via Authorization header)
    api_url = re.sub(r'[?&]access_token=$', '', api_url)

    print("Fetching API: " + api_url, file=sys.stdout)

    if log:
        print_log(api_url)

    try:
        r = requests.get(api_url, headers=headers)
    except ConnectionError:
        print("ERROR: api.laji.fi complete error.", file=sys.stdout)

    if r.status_code == 403:
        print("ERROR: api.laji.fi 403 error.", file=sys.stdout)
        raise ConnectionError

    dataJson = r.text
    dataDict = json.loads(dataJson)

    return dataDict


def fetch_api(api_url, log = False):
    if log:
        print_log(api_url)

    try:
        r = requests.get(api_url)
    except ConnectionError:
        print(f"ERROR: complete error: {api_url}", file = sys.stdout)

#    r.encoding = encoding
    dataJson = r.text
    dataDict = json.loads(dataJson)

    if "status" in dataDict:
        if 403 == dataDict["status"]:
            print(f"ERROR: 403 error: {api_url}", file = sys.stdout)
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


def valid_qname(qname):
    pattern = r'[A-Z]+\.[A-Z0-9]+'
    match = re.fullmatch(pattern, qname)

    if match is not None:
        return qname
    else:
        print_log("ERROR: Qname invalid: " + qname)
        raise ValueError


def taxon_data(taxon_qname):

    url = f"https://api.laji.fi/taxa/{ taxon_qname }?lang=fi&langFallback=true&maxLevel=0&includeHidden=false&includeMedia=false&includeDescriptions=false&includeRedListEvaluations=false&sortOrder=taxonomic"
    data = fetch_finbif_api(url)

    taxon_data = dict()
    # TODO: prepare for no vernacular name
    taxon_data['sci_name'] = data.get('scientificName', 'no name')
    taxon_data['fi_name'] = data.get('vernacularName', '')
    taxon_data['is_cursive'] = data.get('cursiveName', False)

    if data['cursiveName']:
        taxon_data['display_name'] = f"{ taxon_data['fi_name'].capitalize() } (<em>{ taxon_data['sci_name'] }</em>)"
    else:
        taxon_data['display_name'] = f"{ taxon_data['fi_name'].capitalize() } ({ taxon_data['sci_name'] })"

    return taxon_data

