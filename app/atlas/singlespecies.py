import re
import json

import atlas.common_atlas as common_atlas
from helpers import common_helpers

def valid_species_name(species_name_untrusted):    
    pattern = r"[a-zA-ZäöÄÖ]+"
    match = re.fullmatch(pattern, species_name_untrusted)

    if match is not None:
        species_name = species_name_untrusted.lower()
#        species_name = species_name.capitalize()
        return species_name
    else:
        common_helpers.print_log("ERROR: Lajinimi ei kelpaa")
        raise ValueError

def read_json_to_dict(filename):
    filename = "./data/" + filename
    f = open(filename)       
    dictionary = json.load(f)
    f.close()
    return dictionary


def get_confirmed_atlascode_counts(taxon_id):
    # TODO: add quality classes
    time = "2022%2F2025"
    time = "2000%2F2025"

    url = f"https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=unit.atlasCode&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=100&page=1&cache=false&taxonId={taxon_id}&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&time={time}&individualCountMin=1&qualityIssues=NO_ISSUES&reliability=RELIABLE,UNDEFINED&atlasClass=MY.atlasClassEnumD&access_token=";

    data_dict = common_helpers.fetch_finbif_api(url)

    html = "<table class='styled-table'>"
    html += "<thead><tr><th>Pesimävarmuusindeksi</th><th>Havaintoja kpl</th></tr></thead>"

    for item in data_dict["results"]:
        atlas_code = item["aggregateBy"]["unit.atlasCode"]
        atlas_code_text = common_atlas.atlas_code_to_text(atlas_code)

        # Skip erroneous atlas codes
        if False == atlas_code_text:
            continue
        # Skip inaccurate atlas code's
        if "http://tun.fi/MY.atlasCodeEnum7" == atlas_code:
            continue
        if "http://tun.fi/MY.atlasCodeEnum8" == atlas_code:
            continue

        html += "\n<tr><td>" + common_atlas.atlas_code_to_text(atlas_code) + "</td>"
        html += "<td>" + str(item["count"]) + "</td></tr>"

    html += "</table>"
    return html


def get_atlasclass_counts(taxon_id):
    url = f"https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=unit.atlasClass&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=100&page=1&cache=false&taxonId={taxon_id}&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&time=2022%2F2025&individualCountMin=1&qualityIssues=NO_ISSUES&reliability=RELIABLE,UNDEFINED&access_token=";

    data_dict = common_helpers.fetch_finbif_api(url)

    html = "<table class='styled-table'>"
    html += "<thead><tr><th>Pesimävarmuusluokka</th><th>Havaintoja kpl</th></tr></thead>"
    total = 0

    for item in data_dict["results"]:
        if "http://tun.fi/MY.atlasClassEnumB" == item["aggregateBy"]["unit.atlasClass"]:
            html += "<tr><td>Mahdollinen</td>"
            html += "<td>" + str(item["count"]) + "</td></tr>"
            total = total + item["count"]
        elif "http://tun.fi/MY.atlasClassEnumC" == item["aggregateBy"]["unit.atlasClass"]:
            html += "<tr><td>Todennäköinen</td>"
            html += "<td>" + str(item["count"]) + "</td></tr>"
            total = total + item["count"]
        elif "http://tun.fi/MY.atlasClassEnumD" == item["aggregateBy"]["unit.atlasClass"]:
            html += "<tr><td>Varma</td>"
            html += "<td>" + str(item["count"]) + "</td></tr>"
            total = total + item["count"]

    html += f"<tr><td><strong>Yhteensä</strong></td><td><strong>{total}</strong></td></tr>\n"
    html += "</table>"

    return html, total

def get_neighbour_names(this_name):
    atlas_species_data = read_json_to_dict("atlas-species.json")

    names_list = list(atlas_species_data.keys())

    i = 0
    last = len(names_list) - 1

    for name in names_list:
        if name == this_name:
            if 0 == i:
                prev = names_list[last]
                next = names_list[i+1]
            elif last == i:
                prev = names_list[i-1]
                next = names_list[0]
            else:
                prev = names_list[i-1]
                next = names_list[i+1]
            break
        i = i + 1

    return prev, next


def get_notes(taxon_id):
    url = f"https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=unit.notes&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=500&page=1&cache=false&taxonId={taxon_id}&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&taxonRankId=MX.species&countryId=ML.206&time=2022%2F2025&individualCountMin=1&qualityIssues=NO_ISSUES&reliability=RELIABLE,UNDEFINED&atlasClass=MY.atlasClassEnumD&access_token="

    # MY.atlasClassEnumB%2CMY.atlasClassEnumC%2C

    data_dict = common_helpers.fetch_finbif_api(url)

    html = "<table class='styled-table'>"
    html += "<thead><tr><th>Lisätiedot</th><th>Havaintoja kpl</th></tr></thead>"

    for item in data_dict["results"]:
        notes = item["aggregateBy"]["unit.notes"]

        # TODO: Filter out ATL:[0-9]{1-2}, GRI... trim, and skip empties 
        # Skip unimportant notes, like < 4 chars
#        if "http://tun.fi/MY.atlasCodeEnum7" == atlas_code:
#            continue

        html += "\n<tr><td>" + notes + "</td>"
        html += "<td>" + str(item["count"]) + "</td></tr>"

    html += "</table>"
    return html


def day_of_year_NEW(day, month):
    days_in_month = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]
    return days_in_month[month - 1] + day

def day_of_year(day, month):
    days_in_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return sum(days_in_month[:month]) + day


def get_phenology(taxon_id, params):

    year = "2022/2023" # Todo: change to 2022/2024 at the end of 2024.

    url = f"https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=gathering.conversions.day%2Cgathering.conversions.month&onlyCount=true&taxonCounts=false&gatheringCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=366&page=1&cache=false&taxonId={ taxon_id }&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&individualCountMin=1&qualityIssues=NO_ISSUES&reliability=RELIABLE,UNDEFINED{ params }&yearMonth={ year }&access_token="

    data_dict = common_helpers.fetch_finbif_api(url)
#    print(data_dict)

    # Generate dictionary of days of year and number of observations
    day_data = dict()
    for day in data_dict["results"]:
        monthday_number = day["aggregateBy"]["gathering.conversions.day"]
        month_number = day["aggregateBy"]["gathering.conversions.month"]

        # Skip if number is missing
        if "" == monthday_number or "" == month_number:
            continue

        monthday_number = int(monthday_number)
        month_number = int(month_number)

#        print(monthday_number)
#        print(month_number)
        day_data[day_of_year(monthday_number, month_number)] = day["count"]
    
    print(day_data)

    # Fill in missing dates and set in order
    full_day_data = []
    for i in range(1, 366):
        if i in day_data:
            full_day_data.append(day_data[i])
        else:
            full_day_data.append(0)

    print(full_day_data)
    return full_day_data


def get_prediction_map_html(species_name):
    # Check if file exists
    filepath = f"./static/atlasmaps_predictions/{species_name}.png"
    try:
        f = open(filepath)
        f.close()
        root_path = f"/static/atlasmaps_predictions/{species_name}.png"
        return f"<span id='predictionmap'><img src='{ root_path }' alt='' title='Lajin ennustettu esiintyminen. Keltainen: korkea todennäköisyys, tummansininen: matala todennäköisyys.'></span>"
    except FileNotFoundError:
        return "<!-- No prediction map for this species -->"


def main(species_name_untrusted):
    species_name = valid_species_name(species_name_untrusted)

    all_species_data = read_json_to_dict("species-data.json")
    species_data = all_species_data.get(species_name, False)

    if not species_data:
        common_helpers.print_log("ERROR: Species not found: " + species_name)
        raise ValueError

    prev_name, next_name = get_neighbour_names(species_name)
#    common_helpers.print_log(prev_name)
#    common_helpers.print_log(next_name)

    all_species_pairs = read_json_to_dict("species-pairs.json")
    species_pairs_dict = all_species_pairs.get(species_name, { "pareja": 0 })
    species_pairs = species_pairs_dict["pareja"]

    if not isinstance(species_pairs, int):
        species_pairs = int(float(species_pairs.replace(",", ".")))

    atlas_classes_html, observations_total = get_atlasclass_counts(species_data["id"])

    if 0 == species_pairs:
        proportion = "(ei voi laskea)"
    else:
        proportion = round(observations_total / species_pairs, 4)

#    common_helpers.print_log(species_data) # debug

    confirmed_atlas_codes = get_confirmed_atlascode_counts(species_data["id"])

    notes = get_notes(species_data["id"])

    phenology_atlas_all = str(get_phenology(species_data["id"], "&atlasClass=MY.atlasClassEnumB%2CMY.atlasClassEnumC%2CMY.atlasClassEnumD"))
    phenology_atlas_confirmed = str(get_phenology(species_data["id"], "&atlasClass=MY.atlasClassEnumD"))

    html = dict()
    html["prediction_map"] = get_prediction_map_html(species_name)
    html["species_name"] = species_name
    html["prev_name"] = prev_name
    html["next_name"] = next_name
    html["notes"] = notes
    html["species_pairs"] = species_pairs
    html["redlist"] = species_data["redlist"]
    html["habitats"] = species_data["habitats"]
    html["atlas_classes_html"] = atlas_classes_html
    html["proportion"] = proportion
    html["confirmed_atlas_codes_html"] = confirmed_atlas_codes
    html["qname"] = species_data["id"]
    html["phenology_atlas_all"] = phenology_atlas_all
    html["phenology_atlas_confirmed"] = phenology_atlas_confirmed

    return html
