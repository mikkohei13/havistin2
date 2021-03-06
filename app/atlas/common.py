import requests
import json
import sys
import re

import app_secrets

def print_log(dict):
    print(dict, sep="\n", file = sys.stdout)


def neighbour_ids(square_id, include_corners = False):
    links = dict()
    latlon = square_id.split(":")
    links["n"] = str(int(latlon[0]) + 1) + ":" + latlon[1]
    links["e"] = latlon[0] + ":" + str(int(latlon[1]) + 1)
    links["s"] = str(int(latlon[0]) -1) + ":" + latlon[1]
    links["w"] = latlon[0] + ":" + str(int(latlon[1]) - 1)

    if include_corners:
        links["ne"] = str(int(latlon[0]) + 1) + ":" + str(int(latlon[1]) + 1)
        links["se"] = str(int(latlon[0]) - 1) + ":" + str(int(latlon[1]) + 1)
        links["sw"] = str(int(latlon[0]) - 1) + ":" + str(int(latlon[1]) - 1)
        links["nw"] = str(int(latlon[0]) + 1) + ":" + str(int(latlon[1]) - 1)

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
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum1"] = "1 Ep??todenn??k??inen pesint??: havaittu lajin yksil??, havainto ei viittaa pesint????n."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum2"] = "2 Mahdollinen pesint??: yksitt??inen lintu kerran, on sopivaa pesim??ymp??rist????."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum3"] = "3 Mahdollinen pesint??: pari kerran, on sopivaa pesim??ymp??rist????."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum4"] = "4 Todenn??k??inen pesint??: koiras reviirill?? (esim. laulaa) eri p??ivin??."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum5"] = "5 Todenn??k??inen pesint??: naaras tai pari reviirill?? eri p??ivin??."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum6"] = "6 Todenn??k??inen pesint??: linnun tai parin havainto viittaa vahvasti pesint????n."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum61"] = "61 Todenn??k??inen pesint??: lintu tai pari k??y usein todenn??k??isell?? pes??paikalla."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum62"] = "62 Todenn??k??inen pesint??: lintu tai pari rakentaa pes???? tai vie pes??materiaalia."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum63"] = "63 Todenn??k??inen pesint??: lintu tai pari varoittelee ehk?? pes??st?? tai poikueesta."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum64"] = "64 Todenn??k??inen pesint??: lintu tai pari houkuttelee pois ehk?? pes??lt?? / poikueelta."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum65"] = "65 Todenn??k??inen pesint??: lintu tai pari hy??kk??ilee, l??hell?? ehk?? pes?? / poikue."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum66"] = "66 Todenn??k??inen pesint??: n??hty pes??, jossa samanvuotista rakennusmateriaalia tai ravintoj??tett??, ei kuitenkaan varmaa todistetta munista tai poikasista"
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum7"] = "7 Varma pesint??: havaittu ep??suora todiste varmasta pesinn??st??."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum71"] = "71 Varma pesint??: n??hty pes??ss?? saman vuoden munia, kuoria, j????nteit??. Voi olla ep??onnistunut."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum72"] = "72 Varma pesint??: k??y pes??ll?? pesint????n viittaavasti. Munia / poikasia ei havaita (kolo tms.)."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum73"] = "73 Varma pesint??: juuri lentokykyiset poikaset tai untuvikot oletettavasti ruudulta."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum74"] = "74 Varma pesint??: emo kantaa ruokaa tai poikasten ulosteita, pesint?? oletettavasti ruudulla."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum75"] = "75 Varma pesint??: n??hty pes??ss?? hautova emo"
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum8"] = "8 Varma pesint??: havaittu suora todiste varmasta pesinn??st??."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum81"] = "81 Varma pesint??: kuultu poikasten ????ntely?? pes??ss?? (kolo / pes?? korkealla)."
    atlas_code_dict["http://tun.fi/MY.atlasCodeEnum82"] = "82 Varma pesint??: n??hty pes??ss?? munia tai poikasia."

    # Prepare for incorrect atlasCode's, they exist at least in old Hatikka data
    if atlas_code in atlas_code_dict:
        return atlas_code_dict[atlas_code]
    else:
        print_log("erroneous atlasCode: " + atlas_code)
        return False


def read_json_to_dict(filename):
    filename = "./data/" + filename
    f = open(filename)       
    dictionary = json.load(f)
    f.close()
    return dictionary


def split_atlascode(atlascode_text):
    parts = atlascode_text.split(" ")
    return parts[0]


def convert_atlasclass(atlasclass_raw):
    if atlasclass_raw == "Ep??todenn??k??inen pesint??" or atlasclass_raw == 1:
        return "e"
    elif atlasclass_raw == "Mahdollinen pesint??" or atlasclass_raw == 2:
        return "M"
    elif atlasclass_raw == "Todenn??k??inen pesint??" or atlasclass_raw == 3:
        return "T"
    elif atlasclass_raw == "Varma pesint??" or atlasclass_raw == 4:
        return "V"
    else:
        return atlasclass_raw


def convert_breeding_number(atlas_class_key):
    if "MY.atlasClassEnumA" == atlas_class_key:
        return 0
    if "MY.atlasClassEnumB" == atlas_class_key:
        return 1
    if "MY.atlasClassEnumC" == atlas_class_key:
        return 2
    if "MY.atlasClassEnumD" == atlas_class_key:
        return 3


def get_info_top_html(atlas4_square_info_dict):

    level2 = round(atlas4_square_info_dict['level2'], 1)
    level3 = round(atlas4_square_info_dict['level3'], 1)
    level4 = round(atlas4_square_info_dict['level4'], 1)
    level5 = round(atlas4_square_info_dict['level5'], 1)

    if atlas4_square_info_dict['breeding_sum'] >= atlas4_square_info_dict['level5']:
        current_level = "erinomainen"
    elif atlas4_square_info_dict['breeding_sum'] >= atlas4_square_info_dict['level4']:
        current_level = "hyv??"
    elif atlas4_square_info_dict['breeding_sum'] >= atlas4_square_info_dict['level3']:
        current_level = "tyydytt??v??"
    elif atlas4_square_info_dict['breeding_sum'] >= atlas4_square_info_dict['level2']:
        current_level = "v??ltt??v??"
    elif atlas4_square_info_dict['breeding_sum'] >= atlas4_square_info_dict['level1']:
        current_level = "satunnaishavaintoja"
    else:
        current_level = "ei havaintoja"
    
    square_id = atlas4_square_info_dict["coordinates"]

    html = ""
    html += f"<p id='paragraph3'>Selvitysaste: {current_level}, summa: {atlas4_square_info_dict['breeding_sum']} (rajat: v??ltt??v?? {level2}, tyydytt??v?? {level3}, hyv?? {level4}, erinomainen {level5})</p>"

    return html


def get_atlas4_square_data(square_id):
    square_id = square_id.replace(":", "%3A")
    url = f"https://atlas-api.rahtiapp.fi/api/v1/grid/{square_id}/atlas"

    req = requests.get(url)

    # If square exists
    if 200 == req.status_code:
        data_dict = req.json()
    # If square does not exist
    else:
        data_dict = dict()
        data_dict["data"] = []

    # Square metadata as separate dict, without species
    square_info_dict = data_dict.copy()
    square_info_dict.pop("data", None)

    # Species dict with fi name as key
    species_dict = dict().copy()
    breeding_sum_counter = 0

    for species in data_dict["data"]:
        species_dict[species["speciesName"]] = species
        breeding_sum_counter = breeding_sum_counter + convert_breeding_number(species["atlasClass"]["key"])

    square_info_dict["breeding_sum"] = breeding_sum_counter

    return species_dict, square_info_dict

