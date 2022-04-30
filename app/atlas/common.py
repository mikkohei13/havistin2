import requests
import json
import sys
import re

import app_secrets

def print_log(dict):
    print(dict, sep="\n", file = sys.stdout)


def valid_square_id(square_id):
    pattern = r'[6-7][0-9][0-9]:[3-3][0-7][0-9]'
    match = re.fullmatch(pattern, square_id)

    if match is not None:
        return square_id
    else:
        print_log("ERROR: Coordinates invalid.")
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
