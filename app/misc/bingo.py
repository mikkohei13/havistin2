# Controller for a page that displays bird bingo grid, adapted based on time of year and location 


import random

from helpers import common_helpers


def get_species(coordinate_square_id):
    square_id = coordinate_square_id.replace(":", "%3A")

    # Todo: replace hacky url with a proper function
    data = common_helpers.fetch_finbif_api(f"https://atlas-api-dev.rahtiapp.fi/api/v1/taxon/biomon/Mappa/{ square_id }?random=", False)
    return data


def remove_top_n_species(species, n):
    return species[n:]


def fix_name(name):
    if name == "kalliokyyhky":
        return "kesykyyhky"
    if name == "pikkukäpylintu":
        return "käpylintu (suku)"
    if name == "isokäpylintu":
        return "käpylintu (suku)"

    return name


def generate_species_grid(all_species):
    '''
    all_species is like this:
    [
        {
            'vernacularName': {'fi': 'talitiainen', 'sv': 'talgoxe', 'en': 'Great Tit'},
            'scientificName': 'Parus major',
            'taxonomicOrder': 59908,
            'id': 'MX.34567',
            'sensitive': False,
            'intellectualRights': 'MZ.intellectualRightsCC-BY-4.0'
        },
        {
            'vernacularName': {'fi': 'viherpeippo', 'sv': 'grönfink', 'en': 'European Greenfinch'},
            'scientificName': 'Carduelis chloris',
            'taxonomicOrder': 60613,
            'id': 'MX.36283',
            'sensitive': False,
            'intellectualRights': 'MZ.intellectualRightsCC-BY-4.0'
        }
    ]
    '''

    group_a = all_species[:5]  # Most common species
    group_b = all_species[5:9]  # Less common species
    
    # Shuffle the groups to randomize their order
    random.shuffle(group_a)
    random.shuffle(group_b)
    
    # Create the bingo grid
    grid = [None] * 9
    
    # Assigning Group A words to corners and center
    for i in [0, 2, 4, 6, 8]:  # Corners and center positions in the list
        name = group_a.pop(0)["vernacularName"]["fi"]
        grid[i] = fix_name(name)
    
    # Assigning Group B words to the remaining positions
    for i in [1, 3, 5, 7]:  # Remaining positions
        name = group_b.pop(0)["vernacularName"]["fi"]
        grid[i] = fix_name(name)
    
    return grid


def main():
    html = dict()

    coordinate_square_id = "77:35" # Nuorgam
    coordinate_square_id = "71:35" # Kajaani
    coordinate_square_id = "66:30" # Eckerö
    coordinate_square_id = "66:33" # Espoo

    all_species = get_species(coordinate_square_id)

    # Increase difficulty by removing the most common species
    all_species = remove_top_n_species(all_species, 10)

    html["species_grid"] = generate_species_grid(all_species)

    html["title"] = "Bingo"

    return html

