from xml.sax.handler import property_dom_node
import requests
import json

from datetime import datetime, date, timedelta

import finnish_species
import atlas.common as common

def count_species_sum(species_list):
    count_sum = 0
    for species in species_list:
        count_sum = count_sum + species["count"]
    
    return count_sum

def make_coordinates_param(square_id):
    intersect_ratio = 0.1   # decimal 0-1
    shift = 3               # integer >= 1

    square_pieces = square_id.split(":")

    N = int(square_pieces[0])
    E = int(square_pieces[1])

    N_min = N - shift
    N_max = N + shift
    E_min = E - shift
    E_max = E + shift

    coordinates_param = f"{N_min}:{N_max}:{E_min}:{E_max}:YKJ:{intersect_ratio}"

    return coordinates_param


def make_season_param():
    shift = 14

    date_now = date.today()
    season_start = (date_now - timedelta(days = shift)).strftime('%m%d')
    season_end = (date_now + timedelta(days = shift)).strftime('%m%d')
#    print(date_now, season_start, season_end) # debug

    return f"{season_start}/{season_end}"


def adaptive_species(square_id):
    limit = 250
    proportion = 0.0015

    coordinates_param = make_coordinates_param(square_id)
    season_param = make_season_param()

    # All bird data except TIPU
    api_url = f"https://laji.fi/api/warehouse/query/unit/aggregate?target=MX.37580&countryId=ML.206&collectionIdNot=HR.48&typeOfOccurrenceId=MX.typeOfOccurrenceBirdLifeCategoryA,MX.typeOfOccurrenceBirdLifeCategoryC&coordinates={coordinates_param}&aggregateBy=unit.linkings.taxon.speciesId,unit.linkings.taxon.speciesNameFinnish&selected=unit.linkings.taxon.speciesNameFinnish&cache=true&page=1&pageSize={limit}&season={season_param}&geoJSON=false&onlyCount=true&access_token="

    data_dict = common.fetch_finbif_api(api_url)

    species_count_sum = count_species_sum(data_dict["results"])

#    print(f"Sum: {species_count_sum}")

    species_count_dict = dict()

    for species in data_dict["results"]:
        speciesFi = species["aggregateBy"]["unit.linkings.taxon.speciesNameFinnish"]
        count = species["count"]

        # Todo: add birds of prey

        if count > (species_count_sum * proportion):
            species_count_dict[speciesFi] = count

    return species_count_dict


def atlas_species():
    filename = "./data/atlas-species.json"
    f = open(filename)       

    species_dict = json.load(f)

    f.close()
    return species_dict


def atlas3_square(square_id):
    square_id_text = square_id.replace(":", "-")
    filename = f"./data/atlas3/{square_id_text}.json"   

    try:
        f = open(filename)
    except ValueError:
        common.print_log("ERROR: Square file not found.")

    species_dict = json.load(f)
    
    f.close()
    return species_dict


# Most common specis breeding now (-14 days)
def atlas4_breeding():

    # Todo: make a neraby search instead, if there's more data. Use c. 200 km radius.
    # Todo maybe: Make a season search instead, in 2023 when there's data from multiple years. More data and also from future eeks, but not customized for this year.

    number_of_species = "25"

    # Only confirmed breeders
#    url = "https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=unit.linkings.originalTaxon.speciesNameFinnish&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=" + number_of_species + "&page=1&cache=true&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&yearMonth=2022%2F2025&individualCountMin=1&qualityIssues=NO_ISSUES&time=-14%2F0&atlasClass=MY.atlasClassEnumD&access_token=" + app_secrets.finbif_api_token

    # Both probable and confirmed breeders
#    url = "https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=unit.linkings.originalTaxon.speciesNameFinnish&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=" + number_of_species + "&page=1&cache=true&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&yearMonth=2022%2F2025&individualCountMin=1&qualityIssues=NO_ISSUES&time=-14%2F0&atlasClass=MY.atlasClassEnumC,atlasClass=MY.atlasClassEnumD&access_token=" + app_secrets.finbif_api_token

    # Both probable and confirmed breeders, but not 4 & 5, using atlasCode
    api_url = f"https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=unit.linkings.originalTaxon.speciesNameFinnish&onlyCount=true&taxonCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize={number_of_species}&page=1&cache=true&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&yearMonth=2022%2F2025&individualCountMin=1&qualityIssues=NO_ISSUES&time=-14%2F0&atlasCode=MY.atlasCodeEnum6,MY.atlasCodeEnum61,MY.atlasCodeEnum62,MY.atlasCodeEnum63,MY.atlasCodeEnum64,MY.atlasCodeEnum65,MY.atlasCodeEnum66,MY.atlasCodeEnum7,MY.atlasCodeEnum71,MY.atlasCodeEnum72,MY.atlasCodeEnum73,MY.atlasCodeEnum74,MY.atlasCodeEnum75,MY.atlasCodeEnum8,MY.atlasCodeEnum81,MY.atlasCodeEnum82&access_token="

    data_dict = common.fetch_finbif_api(api_url)

    breeding_species_list = [] 

    for species in data_dict['results']:
        breeding_species_list.append(species["aggregateBy"]["unit.linkings.originalTaxon.speciesNameFinnish"])

    return breeding_species_list


def species_html(species_to_show_dict, atlas3_species_dict, atlas4_species_dict, breeding_species_list):

    html = "<div id='listwrapper'>"
    html += "<div class='row header'><div class='species'>Laji</div><div class='atlas3'>3.</div><div class='atlas4'>4.</div><div class='own'>Oma hav.</div></div>"

#    for speciesFi in all_species_dict:
    for speciesFi in finnish_species.list:
        # all_species_dict['speciesFi']

        if speciesFi in species_to_show_dict:

            row_class = ""

            # Atlas 3 data
            atlas3_class = "&nbsp;"
            atlas3_code = "&nbsp;"
            if speciesFi in atlas3_species_dict:
                atlas3_class = common.convert_atlasclass(atlas3_species_dict[speciesFi]["breedingCategory"])
                atlas3_code = str(atlas3_species_dict[speciesFi]["breedingIndex"]).replace("0", "")

            row_class += f" atlas3_class_{atlas3_class}"

            # Atlas 4 data
            atlas4_class = "&nbsp;"
            atlas4_code = "&nbsp;"
            if speciesFi in atlas4_species_dict:
                atlas4_class = common.convert_atlasclass(atlas4_species_dict[speciesFi]["atlasClass"]["value"])
                atlas4_code = str(common.split_atlascode(atlas4_species_dict[speciesFi]["atlasCode"]["value"]))

            row_class += f" atlas4_class_{atlas4_class}"

            # Breeding species
            if speciesFi in breeding_species_list:
                row_class += " breeding_now"
            else:
                row_class += " "

            # HTML
            html += f"<div class='row {row_class}'>"
            html += f"<div class='species'>{speciesFi}</div>"
            html += f"<div class='atlas3'>{atlas3_class}</div>"
            html += f"<div class='atlas4'>{atlas4_code}</div>"
            html += "<div class='own'>&nbsp;</div>"

            html += "</div>"

    html += "</div>"

    return html


def info_top_html(atlas4_square_info_dict):

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
    
    square_id = atlas4_square_info_dict["coordinates"]

    html = ""
    html += f"<p id='paragraph3'>Selvitysaste: {current_level}, summa: {atlas4_square_info_dict['breeding_sum']} (rajat: välttävä {level2}, tyydyttävä {level3}, hyvä {level4}, erinomainen {level5})</p>"

    return html


def showselection_html(square_id):

    html = f"<p>Näytä: <a href='./vakio'>Suomen pesimälajit</a> / <a href='./mukautuva'>seudulla tähän vuodenaikaan havaitut lajit</a></p>"

    return html


def info_bottom_html(show_untrusted, species_count = 250):
    html = ""
    if "mukautuva" == show_untrusted:
        html += f"Tällä lomakkeella on {species_count} yleisimmin tällä alueella tähän vuodenaikaan havaittua lajia. Jos teet täydellisen listan, muista merkitä muistiin myös harvinaisemmat lajit."
    else:
        html += f"Tällä lomakkeella on {species_count} pesimälintulajia. Jos teet täydellisen listan, muista merkitä muistiin myös muut lajit, kuten läpimuuttajat ja harvinaisuudet."
    return html


def main(square_id_untrusted, show_untrusted):
    html = dict()

    square_id = common.valid_square_id(square_id_untrusted)
    html["square_id"] = square_id

    neighbour_ids = common.neighbour_ids(square_id)
    html["neighbour_ids"] = neighbour_ids

    if "mukautuva" == show_untrusted:
        species_to_show_dict = adaptive_species(square_id)
        html["show"] = "mukautuva"
    else:
        species_to_show_dict = atlas_species()
        html["show"] = "vakio"

    # Atlas 3
    atlas3_species_dict = atlas3_square(square_id)
#    print_r(atlas3_species_dict)
#    exit() # debug

    # Atlas 4
    atlas4_species_dict, atlas4_square_info_dict = common.get_atlas4_square_data(square_id)

#    print_r(atlas4_species_dict)

    # Breeding species
    breeding_species_list = atlas4_breeding()

    html["title"] = f"Atlasruutu {atlas4_square_info_dict['coordinates']}"
    html["species"] = species_html(species_to_show_dict, atlas3_species_dict, atlas4_species_dict, breeding_species_list)

    html["heading"] = f"{atlas4_square_info_dict['coordinates']} {atlas4_square_info_dict['name']} <span> - {atlas4_square_info_dict['birdAssociationArea']['value']}</span>"
    
    html["info_top"] = info_top_html(atlas4_square_info_dict)
    html["showselection"] = showselection_html(atlas4_square_info_dict["coordinates"])
    html["info_bottom"] = info_bottom_html(show_untrusted, len(species_to_show_dict))

    return html


