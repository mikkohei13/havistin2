import requests
import json
import sys
import re

import app_secrets

#TODO: combine generic functions with atlas/common.py

def print_log(dict):
    print(dict, sep="\n", file = sys.stdout)


def valid_qname(qname):
    pattern = r'[A-Z]+\.[A-Z0-9]+'
    match = re.fullmatch(pattern, qname)

    if match is not None:
        return qname
    else:
        print_log("ERROR: Qname invalid: " + qname)
        raise ValueError


def fetch_finbif_api(api_url, log = False):
    api_url = api_url + app_secrets.finbif_api_token
#    print(api_url, file = sys.stdout)

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


def fetch_variable_label(variable):
    api_url = f"http://tun.fi/{variable}?format=json"

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
