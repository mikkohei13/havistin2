import requests
import json
import sys
import re

import app_secrets

#TODO: combine generic functions with atlas/common.py

def print_log(dict):
    print(dict, sep="\n", file = sys.stdout)


def map_status(status):
    if "MX.typeOfOccurrenceStablePopulation" == status:
        return "vakiintunut"
    if "MX.typeOfOccurrenceNotEstablished" == status:
        return "ei vakiintunut"
    if "MX.typeOfOccurrenceAnthropogenic" == status:
        return "ihmisen vaikutuksesta"
    if "MX.typeOfOccurrenceVeryRare" == status:
        return "hyvin harvinainen"
    return status


def valid_qname(qname):
    pattern = r'[A-Z]+\.[A-Z0-9]+'
    match = re.fullmatch(pattern, qname)

    if match is not None:
        return qname
    else:
        print_log("ERROR: Qname invalid: " + qname)
        raise ValueError


def fetch_api(api_url, log = False):
    if log:
        print_log(api_url)
    try:
        r = requests.get(api_url)
    except ConnectionError:
        print("ERROR: API connection error.", file = sys.stdout)
    dataDict = json.loads(r.text)
    if "status" in dataDict:
        if 403 == dataDict["status"]:
            print("ERROR: API 403 error.", file = sys.stdout)
            raise ConnectionError
    return dataDict


def fetch_finbif_api(api_url, log = False):
    api_url = api_url + app_secrets.finbif_api_token
#    print(api_url, file = sys.stdout)

    if log:
        print_log(api_url)

    try:
        r = requests.get(api_url)
    except ConnectionError:
        print("ERROR: api.laji.fi connection error.", file = sys.stdout)

#    r.encoding = encoding
    dataJson = r.text
    dataDict = json.loads(dataJson)

    if "status" in dataDict:
        if 403 == dataDict["status"]:
            print("ERROR: api.laji.fi 403 error.", file = sys.stdout)
            raise ConnectionError

#    print(dataDict, file = sys.stdout)
    return dataDict


# TODO: caching?
def fetch_variable_label(variable):

    variable = variable.replace("http://tun.fi/", "")

    api_url = f"http://tun.fi/{variable}?format=json"

    print_log("HERE")
    print_log(api_url)

    try:
        r = requests.get(api_url)
    except ConnectionError:
        print("ERROR: api.laji.fi complete error.", file = sys.stdout)

    dataJson = r.text
    dataDict = json.loads(dataJson)

    if "status" in dataDict:
        if 403 == dataDict["status"]:
            print("ERROR: api.laji.fi 403 error.", file = sys.stdout)
            raise ConnectionError

    labels = dataDict["label"]
    for label in labels:
        if "fi" == label["@language"]:
            label_fi = label["@value"]
            break

    print(dataDict, file = sys.stdout)
    return label_fi


# TODO: make full list of possible licenses
# TODO: make license link
def cc_abbreviation(lic):
    if "http://tun.fi/MZ.intellectualRightsCC-BY-NC-4.0" == lic or "CC-BY-NC-4.0" == lic or "CC BY-NC 4.0" == lic:
        return "CC BY-NC 4.0"
    if "http://tun.fi/MZ.intellectualRightsCC-BY-SA-4.0" == lic or "CC-BY-SA-4.0" == lic:
        return "CC BY-SA 4.0"
    if "http://tun.fi/MZ.intellectualRightsCC-BY-4.0" == lic or "CC-BY-4.0" == lic:
        return "CC BY 4.0"
    if "http://tun.fi/MZ.intellectualRightsCC-BY-NC-ND-4.0" == lic or "CC-BY-NC-ND-4.0" == lic:
        return "CC BY-NC-ND 4.0"
    if "http://tun.fi/MZ.intellectualRightsCC-BY-NC-SA-4.0" == lic or "CC-BY-NC-SA-4.0" == lic:
        return "CC BY-NC-SA 4.0"
    if "CC0-4.0" == lic:
        return "CC Zero 4.0"

#    if "" == lic or "" == lic:
#        return ""
    return lic

