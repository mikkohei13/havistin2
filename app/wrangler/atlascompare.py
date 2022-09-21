
'''
Tool to compare data from bird atlas and Tiira, to see which species & observations are missing breeding index.

'''

import pandas as pd
import numpy as np
import json 
import sys
import requests


def save_html(html):

    pre_html = """
        <html><head><title>Atlasruudun havainnot</title>
        <style>
            body {
                font-family: Arial, Helvetica, sans-serif;
            }
            h3 {
                padding: 0.5em;
                background-color: #eee;
                position: sticky;
                top: 0;
                z-index: 999;
                font-weight: normal;
            }
            h3 span {
                font-weight: bold;
            }
            h3 strong {
                color: #f00;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            td {
                border: 1px solid #ccc;
                padding: 0.3em;
                vertical-align: top;
            }
            .secret {
                background-color: #f77;
                color: #fff;
            }
            .breeding {
                background-color: #77f;
                color: #fff;
            }
            .nowrap {
                white-space: nowrap;
            }
        </style>
        </head><body>"""

    post_html = "<p>tiira-atlas-compare v20220921</p></body></html>"

    html = pre_html + html + post_html

    path = "./export/ruutu.html"
    text_file = open("./export/ruutu.html", "w")
    n = text_file.write(html)
    text_file.close()
    print(f"Saved {path}")
    return True


def truncate(value, length):
    if len(value) <= length:
        return value
    else:
        return (value[0:length] + "…")


def convert_atlas_code(value):
    return value['key'].replace("MY.atlasCodeEnum", "")


def convert_atlas_class(value):
    atlas_class = value['key'].replace("MY.atlasClassEnum", "")
    return atlas_class

def get_square_atlas_dict(square):
    square = square.replace(":", "%3A")
    api_url = f"https://atlas-api.rahtiapp.fi/api/v1/grid/{square}/atlas"

    try:
        r = requests.get(api_url)
    except ConnectionError:
        print("ERROR: API error.", file = sys.stdout)

#    r.encoding = encoding
    data_json = r.text
    data_dict = json.loads(data_json)

    indexed_dict =  {}

    for species in data_dict['data']:
#        print(species)
        indexed_dict[species['speciesName']] = {}
        indexed_dict[species['speciesName']]['atlas_code'] = convert_atlas_code(species['atlasCode'])
        indexed_dict[species['speciesName']]['atlas_class'] = convert_atlas_class(species['atlasClass'])

    return indexed_dict


def migrating(status):
    status_string = str(status)
    status_pieces = status_string.split(", ")

    migrating_statuses = ["m", "N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    migrating = any(item in status for item in migrating_statuses)

#    if "m" in status_pieces:
    if migrating:
        if "p" in status_pieces:
            return False
        return True
    return False


def atlascode(value):
    if "" == value:
        return ""
    else:
        return "ATL:" + str(int(value))


print("------ START ------------------------------------------------------------")

sensitive_species = ['kiljuhanhi', 'merikotka', 'kiljukotka', 'sääksi', 'maakotka', 'tunturihaukka', 'muuttohaukka', 'lapinsirri', 'etelänsuosirri', 'rantakurvi', 'tunturipöllö', 'kuukkeli', 'punakuiri', 'etelänkiisla']

atlas_square = "667:337"
atlas_dict = get_square_atlas_dict(atlas_square)

#print(atlas_dict)

# Source data - Tiira export saved as UTF-8 CSV file
tiira_filename = "./import/tiira.csv"

tiira_df = pd.read_csv(tiira_filename, sep=";")
tiira_df = tiira_df.replace(np.nan, "", regex=True)

html = f"<h1>{atlas_square}</h1>"
html += "<div><table>"

limit = 10000
i = 0
s = 0
#html += "<div class='species'><table>"

species_mem = ""
for ind in tiira_df.index:

    # Use bird coordinates if present, otherwise observer coordinates
    if tiira_df['Y-koord-linnun'][ind]:
        bird_has_coordinates = True
        n = str(tiira_df['Y-koord-linnun'][ind])
        e = str(tiira_df['X-koord-linnun'][ind])
    else:
        bird_has_coordinates = False
        n = str(tiira_df['Y-koord'][ind])
        e = str(tiira_df['X-koord'][ind])

    # Skip if wrong square
    if (n[0:3] + ":" + e[0:3]) != atlas_square:
#        print(f"Skipping wrong square: {latlon}")
        continue

    species = tiira_df['Laji'][ind]

    # Harmonize names between Tiira & Atlas
    if "kesykyyhky" == species:
        species = "kalliokyyhky" 

    # Skip if breeding is already certain
    if species in atlas_dict:
        if "D" == atlas_dict[species]['atlas_class']:
            continue

    # Skip migrating
    if migrating(tiira_df['Tila'][ind]):
        continue


    # Skip uncertain species and non-species
    if "/" in species:
        continue

    if "laji" in species:
        continue

    if "risteymä" in species:
        continue

    if " " in species:
        continue

    if "lintu" == species:
        continue

    # Tiira datafile can contain rows without species name, skip them as well.
    if "" == species:
        continue

    # Skip if already probable or certain observation, and this observation does not have any notes, because any information about probable or certain breeding whould be in the notes.
    if species in atlas_dict:
        if "C" == atlas_dict[species]['atlas_class']:
            all_notes = str(tiira_df['Lisätietoja'][ind]) + str(tiira_df['Lisätietoja_2'][ind]) + str(tiira_df['Pesintä'][ind])
            if "" == all_notes:
                continue

    if species != species_mem:
        html += "</table></div>"
        html += "<div class='species'>\n"
        html += "<h3><span>" + species.capitalize() + "</span><br>\n"
        if species not in atlas_dict:
            html += "Ei atlashavaintoja"
        elif "A" == atlas_dict[species]['atlas_class']:
            html += "Epätodennäköinen pesintä"
        elif "B" == atlas_dict[species]['atlas_class']:
            html += "Mahdollinen pesintä"
        elif "C" == atlas_dict[species]['atlas_class']:
            html += "On todennäköinen pesintä"

        if species in sensitive_species:
            html += " <strong>(osa) atlashavainnoista karkeistetaan</strong>"

        html += "</h3>\n<table>\n"
        table_open = True
        species_mem = species

    if "X" == str(tiira_df['Salattu'][ind]):
        secret = "<em class='secret'>salattu</em> "
        s = s + 1
    else:
        secret = ""

    if "X" == str(tiira_df['Pesintä'][ind]):
        breeding = "<em class='breeding'>merkitty pesiväksi</em> "
        s = s + 1
    else:
        breeding = ""


#    print("Now handling obs " + str(tiira_df['Havainto id'][ind]))
    html += "<tr>"
    html += "<td>" + str(tiira_df['Pvm1'][ind]) + "-<br>" + str(tiira_df['Pvm2'][ind]) + "</td>\n"
    html += "<td>" + str(tiira_df['Kunta'][ind]) + " " + str(tiira_df['Paikka'][ind]) + "</td>"
    html += "<td class='nowrap'>" + str(tiira_df['Määrä'][ind]) + " " + str(tiira_df['Tila'][ind]) + "</td>"
    html += "<td>" + secret + breeding + str(tiira_df['Lisätietoja'][ind]) + ", " + str(tiira_df['Lisätietoja_2'][ind]) + "</td>"
    html += "<td>" + atlascode(tiira_df['Atlaskoodi'][ind]) + "</td>"
#    html += "<td>" + str(tiira_df['Y-koord'][ind]) + ":<br>" + str(tiira_df['X-koord'][ind]) + "</td>"
    html += "<td>" + truncate(tiira_df['Havainnoijat'][ind], 20) + "</td>"
    html += "<td><a href='https://www.tiira.fi/selain/naytahavis.php?id=" + str(tiira_df['Havainto id'][ind]) + "' target='_blank' name='tiirahavis'>[↗]</a></td>"
    html += "</tr>\n"

    i = i + 1
    if i > limit:
        break

html += "</table>\n"

html += f"<p class='total'>Yhteensä {i} havaintoa, joista {s} salattuja Tiirassa</p>"

save_html(html)

