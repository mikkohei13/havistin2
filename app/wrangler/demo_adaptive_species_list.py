
import requests
import json

import re

from datetime import datetime, date, timedelta

# IDEA: käyttäjä voi valiuta pesimälajit 250 kpl, tai alueen lajilistan, jossa myös muuttavia (tundrahanhi..) ja rareja.

'''
def to_simple_dict(data_list):
    speciesFi = data_list["aggregateBy"]["unit.linkings.taxon.speciesNameFinnish"]
    count = data_list["count"]
    return { speciesFi: count }
'''

def count_sum(species_list):
    count_sum = 0
    for species in species_list:
        count_sum = count_sum + species["count"]
    
    return count_sum


def valid_square_id(square_id):
    pattern = r'[6-7][0-9][0-9]:[3-3][0-7][0-9]'
    match = re.fullmatch(pattern, square_id)

    if match is not None:
        return True
    else:
        return False
    
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
    shift = 10

    date_now = date.today()
    season_start = (date_now - timedelta(days = shift)).strftime('%m%d')
    season_end = (date_now + timedelta(days = shift)).strftime('%m%d')

#    print(date_now, season_start, season_end) # debug

    return f"{season_start}/{season_end}"


# Settings
limit = 250
square_id = "667:337"

if not valid_square_id(square_id):
    exit("Ruudun koordinaattien pitää olla muodossa nnn:eee (esim. 668:338), sekä Suomen alueella.")

coordinates_param = make_coordinates_param(square_id)
season_param = make_season_param()

# TODO: get date from param & validate
#date = datetime.strptime("2022-01-01", '%Y-%m-%d')

# Both probable and confirmed breeders
url = f"https://laji.fi/api/warehouse/query/unit/aggregate?target=MX.37580&countryId=ML.206&collectionId=HR.1747,HR.3691,HR.4412,HR.4471,HR.3211&typeOfOccurrenceId=MX.typeOfOccurrenceBirdLifeCategoryA,MX.typeOfOccurrenceBirdLifeCategoryC&coordinates={coordinates_param}&aggregateBy=unit.linkings.taxon.speciesId,unit.linkings.taxon.speciesNameFinnish&selected=unit.linkings.taxon.speciesNameFinnish&cache=true&page=1&pageSize={limit}&season={season_param}&geoJSON=false&onlyCount=true" + TOKEN

req = requests.get(url)
data_dict = req.json()

#exit(url)

species_count_sum = count_sum(data_dict["results"])

print(f"Sum: {species_count_sum}")

species_count_dict = dict()

for species in data_dict["results"]:
    speciesFi = species["aggregateBy"]["unit.linkings.taxon.speciesNameFinnish"]
    count = species["count"]

    if count > (species_count_sum * 0.001):
        species_count_dict[speciesFi] = count
    else:
        print(f"left out {speciesFi} with count {count}")

#species_count_dict = map(to_simple_dict, data_dict["results"])

print(species_count_dict)

#for species in data_dict['results']:
#    breeding_species_list.append(species["aggregateBy"]["unit.linkings.originalTaxon.speciesNameFinnish"])
