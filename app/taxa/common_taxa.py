import requests
import json
import sys
import re

from helpers import common_helpers


def map_status(status):
    if status == "MX.typeOfOccurrenceStablePopulation":
        return "vakiintunut"
    if status == "MX.typeOfOccurrenceNotEstablished":
        return "<strong>ei vakiintunut</strong>"
    if status == "MX.typeOfOccurrenceRareVagrant":
        return "<strong>satunnainen harhailija</strong>"
    if status == "MX.typeOfOccurrenceExtirpated":
        return "<strong>hävinnyt</strong>"
    if status == "MX.typeOfOccurrenceVeryRare":
        return "<strong>hyvin harvinainen</strong>"
    if status == "MX.typeOfOccurrenceImport":
        return "<strong>ihmisen tuoma (importti)</strong>"
    if status == "MX.typeOfOccurrenceMigrant":
        return "<strong>vaeltaja</strong>"
    if status == "MX.typeOfOccurrenceAnthropogenic":
        return "<strong>ihmisen vaikutuksesta</strong>"

    return status


def valid_qname(qname):
    pattern = r'[A-Z]+\.[A-Z0-9]+'
    match = re.fullmatch(pattern, qname)

    if match is not None:
        return qname
    else:
        common_helpers.print_log("ERROR: Qname invalid: " + qname)
        raise ValueError

'''
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
'''

# TODO: caching?
def fetch_variable_label(variable):

    variable = variable.replace("http://tun.fi/", "")

    api_url = f"http://tun.fi/{variable}?format=json"

#    common_helpers.print_log(api_url)

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

#    print(dataDict, file = sys.stdout)
    return label_fi

