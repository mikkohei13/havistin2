
'''
Converts taxon-export.tsv file from Laji.fi into json that uses taxon qnames as indexes.
'''

import json
import pandas as pd

def convert_tsv_to_json(file_path, output_json_path):
    # Load the TSV file
    data = pd.read_csv(file_path, sep='\t')

    # Remove unnecessary columns:
    data = data.drop([
        'Pääjakso / kaari, Auktorit',
        'Luokka, Auktorit',
        'Lahko, Auktorit',
        'Heimo, Auktorit'
    ], axis=1)

    # Process the data
    # - Remove the "http://tun.fi/" prefix from "Tunniste"
    # - Rename the columns
    # - Convert 'obs' to integer, replacing NaN with 0
    data['Tunniste'] = data['Tunniste'].str.replace('http://tun.fi/', '')
    data.rename(columns={
        'Suositeltu yleiskielinen nimi': 'fi', 
        'Tieteellinen nimi': 'sci', 
        'Havaintomäärä Suomesta': 'obs',
        'Vieraslaji': 'inv',
        'Suomalainen': 'f',
        'Pääjakso / kaari, Tieteellinen nimi': 'phy',
        'Luokka, Tieteellinen nimi': 'cla',
        'Lahko, Tieteellinen nimi': 'ord',
        'Heimo, Tieteellinen nimi': 'fam',
    }, inplace=True)
    data['obs'] = data['obs'].fillna(0).astype(int)

    # Convert the DataFrame to a dictionary
    json_dict = data.set_index('Tunniste').to_dict(orient='index')

    # Save the dictionary to a JSON file
    with open(output_json_path, 'w') as json_file:
        json.dump(json_dict, json_file, indent=0)

input_file_path = 'taxon-export.tsv'
output_file_path = 'taxon-data.json'

convert_tsv_to_json(input_file_path, output_file_path)
