import requests
import json
import re

from helpers import common_helpers


ai_common_species = [
"kirjosieppo",
"talitiainen",
"sinitiainen",
"peippo",
"tuulihaukka",
"pajulintu",
"punakylkirastas",
"käpytikka",
"räkättirastas",
"mustarastas",
"naurulokki",
"telkkä",
"metsäkirvinen",
"punarinta",
"vihervarpunen",
"laulurastas",
"sepelkyyhky",
"kalalokki",
"västäräkki",
"kottarainen",
"tiltaltti",
"keltasirkku",
"varis",
"leppälintu",
"pikkuvarpunen",
"laulujoutsen",
"haarapääsky",
"töyhtöhyyppä",
"kalatiira",
"käki",
"sinisorsa",
"peukaloinen",
"kurki",
"lehtokerttu",
"hippiäinen",
"kuovi",
"harmaasieppo",
"järripeippo",
"hernekerttu",
"harakka",
"pajusirkku",
"naakka",
"hömötiainen",
"rantasipi",
"viherpeippo",
"korppi",
"viirupöllö",
"pensaskerttu",
"rautiainen",
"palokärki",
"punatulkku",
"harmaalokki",
"tervapääsky",
"kiuru",
"pensastasku",
"puukiipijä",
"mustapääkerttu",
"teeri",
"taivaanvuohi",
"metsäviklo",
"kulorastas",
"töyhtötiainen",
"tavi",
"ruokokerttunen",
"harmaapäätikka",
"kuusitiainen",
"lehtopöllö",
"pyy",
"niittykirvinen",
"urpiainen",
"lehtokurppa",
"räystäspääsky",
"varpunen",
"punavarpunen",
"pikkukäpylintu",
"sirittäjä",
"sääksi",
"helmipöllö",
"kanahaukka",
"silkkiuikku",
"kuikka",
"kivitasku",
"liro",
"närhi",
"varpuspöllö",
"isokoskelo",
"satakieli",
"keltavästäräkki",
"valkoviklo",
"tikli",
"viitakerttunen",
"pikkutikka",
"tukkasotka",
"varpushaukka",
"lapintiira",
"haapana",
"hiirihaukka",
"metso",
"fasaani",
"pikkulepinkäinen",
"selkälokki",
"kyhmyjoutsen",
"pohjansirkku",
"meriharakka",
"merimetso",
"nuolihaukka",
"ruskosuohaukka",
"hemppo",
"kaulushaikara",
"käenpiika",
"kanadanhanhi",
"kultarinta",
"tukkakoskelo",
"uuttukyyhky",
"kehrääjä",
"ruisrääkkä",
"kapustarinta",
"lapintiainen",
"härkälintu",
"mustakurkku-uikku",
"nokikana",
"merikotka",
"punajalkaviklo",
"pikkukuovi",
"pikkulokki",
"törmäpääsky",
"valkoposkihanhi",
"pikkutylli",
"pyrstötiainen",
"haahka",
"merihanhi",
"kalliokyyhky",
"räyskä",
"riekko",
"suopöllö",
"lapasorsa",
"huuhkaja",
"isokäpylintu",
"kaakkuri",
"pikkusieppo",
"pohjantikka",
"mehiläishaukka",
"tilhi",
"sarvipöllö",
"valkoselkätikka",
"merilokki",
"tylli",
"luhtakerttunen",
"uivelo",
"luhtakana",
"kangaskiuru",
"harmaasorsa",
"sinisuohaukka",
"kuukkeli",
"pilkkasiipi",
"peltopyy",
"maakotka",
"isolepinkäinen",
"rytikerttunen",
"turkinkyyhky",
"jouhisorsa",
"pensassirkkalintu",
"mustapyrstökuiri",
"sinipyrstö",
"lapinpöllö",
"sinirinta",
"suokukko",
"muuttohaukka",
"liejukana",
"harmaahaikara",
"peltosirkku",
"merikihu",
"metsähanhi",
"riskilä",
"ampuhaukka",
"punasotka",
"pähkinänakkeli",
"lapinsirkku",
"nokkavarpunen",
"luotokirvinen",
"ruokki",
"idänuunilintu",
"luhtahuitti",
"pähkinähakki",
"mustaviklo",
"jänkäkurppa",
"heinätavi",
"taviokuurna",
"rastaskerttunen",
"karikukko",
"piekana",
"virtavästäräkki",
"etelänkiisla",
"ristisorsa",
"kirjosiipikäpylintu",
"koskikara",
"viitasirkkalintu",
"lapinsirri",
"hiiripöllö",
"suosirri",
"tunturikihu",
"vesipääsky",
"mustavaris",
"pikkusirkku",
"mustalintu",
"arosuohaukka",
"viiriäinen",
"mustaleppälintu",
"viiksitimali",
"keräkurmitsa",
"kuhankeittäjä",
"kiiruna",
"jänkäsirriäinen",
"pulmunen",
"sitruunavästäräkki",
"ruokosirkkalintu",
"punakuiri",
"alli",
"pikkutiira",
"sepelrastas",
"kuningaskalastaja",
"jalohaikara",
"haarahaukka",
"lapasotka",
"tulipäähippiäinen",
"lapinuunilintu",
"tundraurpiainen",
"kirjokerttu",
"lapinkirvinen",
]

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
        common_helpers.print_log("ERROR: Coordinates invalid")
        raise ValueError


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

    data_dict = common_helpers.fetch_finbif_api(api_url, False)

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

    # Prepare for incorrect atlasCode's, they exist at least in old Hatikka data
    if atlas_code in atlas_code_dict:
        return atlas_code_dict[atlas_code]
    else:
        common_helpers.print_log("erroneous atlasCode: " + atlas_code)
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
    if atlasclass_raw == "Epätodennäköinen pesintä" or atlasclass_raw == 1:
        return "e"
    elif atlasclass_raw == "Mahdollinen pesintä" or atlasclass_raw == 2:
        return "M"
    elif atlasclass_raw == "Todennäköinen pesintä" or atlasclass_raw == 3:
        return "T"
    elif atlasclass_raw == "Varma pesintä" or atlasclass_raw == 4:
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
        current_level = "hyvä"
    elif atlas4_square_info_dict['breeding_sum'] >= atlas4_square_info_dict['level3']:
        current_level = "tyydyttävä"
    elif atlas4_square_info_dict['breeding_sum'] >= atlas4_square_info_dict['level2']:
        current_level = "välttävä"
    elif atlas4_square_info_dict['breeding_sum'] >= atlas4_square_info_dict['level1']:
        current_level = "satunnaishavaintoja"
    else:
        current_level = "ei havaintoja"
    
#    square_id = atlas4_square_info_dict["coordinates"]

    until_satisfactory = level3 - atlas4_square_info_dict['breeding_sum']
    if until_satisfactory < 0:
        until_satisfactory = 0
    else:
        until_satisfactory = round(until_satisfactory, 2)

    satisfactory_proportion = (atlas4_square_info_dict['breeding_sum'] / level3) * 100
    satisfactory_proportion = round(satisfactory_proportion, 1)

    html = ""
    html += f"<p id='paragraph3'>Selvitysaste <strong>{current_level}, summa {atlas4_square_info_dict['breeding_sum']}</strong>, rajat: välttävä {level2}, tyydyttävä {level3}, hyvä {level4}, erinomainen {level5}.<br>Summasta puuttuu tyydyttävään {until_satisfactory}, <strong>tyydyttävästä saavutettu {satisfactory_proportion} %</strong></p>"

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



def get_species_predictions(square_id, year):
    square_filename = square_id.replace(":", "_")
    filename = f"./data/atlas_predictions_{ year }/{ square_filename }.json"
    f = open(filename)       

    species_dict = json.load(f)

    f.close()
    return species_dict


def atlas_class_to_value(class_value):
    if "MY.atlasClassEnumA" == class_value:
        return 0
    if "MY.atlasClassEnumB" == class_value:
        return 1
    if "MY.atlasClassEnumC" == class_value:
        return 2
    if "MY.atlasClassEnumD" == class_value:
        return 3
    return 0


def get_species_missvalues(species_predictions, atlas4_species):

    # Count missvalues
    missvalues = dict()

    for species, data in species_predictions.items():

        # Ignore too improbable species
        if data["predictions"][0]["value"] < 0.5:
            continue

        # Get capped predicted class
        predicted_class = data["predictions"][0]["value"]
        if predicted_class < 0:
            predicted_class = 0
        elif predicted_class > 3:
            predicted_class = 3

        # If observed in 4th atlas, calculate difference
        if species in atlas4_species:
            current_class = atlas_class_to_value(atlas4_species[species]["atlasClass"]["key"])
            missvalue = predicted_class - current_class

            # if already higher than predicted value
            if missvalue < 0:
                missvalue = 0

            missvalue = round(missvalue, 1)
            
        # if not observed, just use predicted value
        else:
            missvalue = round(predicted_class, 1)

        # Add to the list, if missvalue is significant
        if missvalue > 0.1:
            missvalues[species] = missvalue

    return missvalues
