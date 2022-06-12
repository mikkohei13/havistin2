import requests
import json
import sys
import re

import app_secrets

def print_log(dict):
    print(dict, sep="\n", file = sys.stdout)


def neighbour_ids(square_id):
    links = dict()
    latlon = square_id.split(":")
    links["n"] = str(int(latlon[0]) + 1) + ":" + latlon[1]
    links["e"] = latlon[0] + ":" + str(int(latlon[1]) + 1)
    links["s"] = str(int(latlon[0]) -1) + ":" + latlon[1]
    links["w"] = latlon[0] + ":" + str(int(latlon[1]) - 1)

    return links

def valid_square_id(square_id):
    pattern = r'[6-7][0-9][0-9]:[3-3][0-7][0-9]'
    match = re.fullmatch(pattern, square_id)

    if match is not None:
        return square_id
    else:
        print_log("ERROR: Coordinates invalid: " + square_id)
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


# This fixes data that's in string format in the json file
def str2decimal(str):
    str = str.replace(",", ".")
    return str


def square_info(square_id):
    with open("data/atlas-grids.json") as f:
        data = json.load(f)

    # Todo: streamline, use file per square?
    # Todo: validate that square exists. Test case: 677:377
    d = data[square_id]

    name = d["kunta"] + ", " + d["nimi"]

    society = d["yhd"]

    centerpoint = str2decimal(d["c-n"]) + "," + str2decimal(d["c-e"])

    cornerpoints = "[" + str(d["sw-n"]) + "," + str(d["sw-e"]) + "], [" + str(d["nw-n"]) + "," + str(d["nw-e"]) + "], [" + str(d["ne-n"]) + "," + str(d["ne-e"]) + "], [" + str(d["se-n"]) + "," + str(d["se-e"]) + "], [" + str(d["sw-n"]) + "," + str(d["sw-e"]) + "]"

    return name, society, centerpoint, cornerpoints


def square_name(square_id):
    # Todo: simplify?
    name, society, centerpoint, cornerpoints = square_info(square_id)
    return name


def coordinate_accuracy_data(square_id = False):
    if square_id:
        coordinates = f"&coordinates={square_id}%3AYKJ"
    else:
        coordinates = ""
    
    api_url = f"https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=gathering.interpretations.coordinateAccuracy{coordinates}&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=100&page=1&cache=false&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&yearMonth=2022%2F2025&individualCountMin=1&qualityIssues=NO_ISSUES&atlasClass=MY.atlasClassEnumB%2CMY.atlasClassEnumC%2CMY.atlasClassEnumD&access_token="

    data_dict = fetch_finbif_api(api_url, False)

    accuracy_dict = dict()
    total_count = 0
    for item in data_dict["results"]:
        accuracy_text = ""        
        accuracy = int(item["aggregateBy"]["gathering.interpretations.coordinateAccuracy"])
        count = item["count"]
        total_count = total_count + count

        if accuracy == 1:
            accuracy_text = "1"
        elif accuracy <= 10:
            accuracy_text = "10"
        elif accuracy <= 100:
            accuracy_text = "100"
        elif accuracy <= 1000:
            accuracy_text = "1000"
        elif accuracy <= 5000:
            accuracy_text = "5000"
        elif accuracy <= 10000:
            accuracy_text = "10000"
        elif accuracy <= 25000:
            accuracy_text = "25000"
        else:
            accuracy_text = "over"

        # Todo: better way to do this?    
        if accuracy_text in accuracy_dict:
            accuracy_dict[accuracy_text] = accuracy_dict[accuracy_text] + count
        else:
            accuracy_dict[accuracy_text] = count

    return accuracy_dict, total_count

def atlas_code_to_text(atlas_code):
    atlas_code_dict = dict()
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum1"] = "1 Epätodennäköinen pesintä: havaittu lajin yksilö, havainto ei viittaa pesintään."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum2"] = "2 Mahdollinen pesintä: yksittäinen lintu kerran, on sopivaa pesimäympäristöä."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum3"] = "3 Mahdollinen pesintä: pari kerran, on sopivaa pesimäympäristöä."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum4"] = "4 Todennäköinen pesintä: koiras reviirillä (esim. laulaa) eri päivinä."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum5"] = "5 Todennäköinen pesintä: naaras tai pari reviirillä eri päivinä."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum6"] = "6 Todennäköinen pesintä: linnun tai parin havainto viittaa vahvasti pesintään."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum61"] = "61 Todennäköinen pesintä: lintu tai pari käy usein todennäköisellä pesäpaikalla."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum62"] = "62 Todennäköinen pesintä: lintu tai pari rakentaa pesää tai vie pesämateriaalia."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum63"] = "63 Todennäköinen pesintä: lintu tai pari varoittelee ehkä pesästä tai poikueesta."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum64"] = "64 Todennäköinen pesintä: lintu tai pari houkuttelee pois ehkä pesältä / poikueelta."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum65"] = "65 Todennäköinen pesintä: lintu tai pari hyökkäilee, lähellä ehkä pesä / poikue."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum66"] = "66 Todennäköinen pesintä: nähty pesä, jossa samanvuotista rakennusmateriaalia tai ravintojätettä, ei kuitenkaan varmaa todistetta munista tai poikasista"
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum7"] = "7 Varma pesintä: havaittu epäsuora todiste varmasta pesinnästä."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum71"] = "71 Varma pesintä: nähty pesässä saman vuoden munia, kuoria, jäänteitä. Voi olla epäonnistunut."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum72"] = "72 Varma pesintä: käy pesällä pesintään viittaavasti. Munia / poikasia ei havaita (kolo tms.)."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum73"] = "73 Varma pesintä: juuri lentokykyiset poikaset tai untuvikot oletettavasti ruudulta."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum74"] = "74 Varma pesintä: emo kantaa ruokaa tai poikasten ulosteita, pesintä oletettavasti ruudulla."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum75"] = "75 Varma pesintä: nähty pesässä hautova emo"
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum8"] = "8 Varma pesintä: havaittu suora todiste varmasta pesinnästä."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum81"] = "81 Varma pesintä: kuultu poikasten ääntelyä pesässä (kolo / pesä korkealla)."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum82"] = "82 Varma pesintä: nähty pesässä munia tai poikasia."

    return atlas_code_dict[atlas_code]
