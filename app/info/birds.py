

from helpers import common_helpers
import app_secrets

import requests
from bs4 import BeautifulSoup
import re

def fetch_html(url, class_name):
    # Fetch HTML content from the URL
    response = requests.get(url)
    html_doc = response.text

    soup = BeautifulSoup(html_doc, 'html.parser')
    data = soup.find('div', class_=class_name)
    data = str(data) # BS4 object into string

    # Cleanup
    data = data.replace("<div class=\"www-raportti\">", "")
    data_parts = data.split("<br/>Katso havainnot <a")

    return data_parts[0]



def split_observation(text):
    text = text.replace('\xa0', ' ')

    # Pattern to identify text inside and outside of <b> tags
    pattern = r'(<b>.*?</b>|\(.*?\)|[^<\(\)]+)'

    # Find all matches of the pattern in the text
    d = re.findall(pattern, text)

    # Clean
    d[0] = d[0].replace("<b>", "").replace("</b>", "")
    d[1] = d[1].strip()
    d[2] = d[2].replace("<b>", "").replace("</b>", "")
    d[3] = d[3].strip()
    d[4] = d[4][1:-1]

    return d


def parse_html(html_content):
    observations = []
    rows = html_content.split("<br/>")

    # Todo: this breaks if other than person names are in parenthesis 
    # Replace second to last "(" with "<b>"?

    # Pattern to match <b>D(D).M(M).</b>
    pattern = r'^<b>(\d{1,2})\.(\d{1,2})\.</b>$'

    i = 0
    date_mem = ""
    for row in rows:
        row = row.strip()
        i += 1
        # Date
        if bool(re.match(pattern, row)):
            date_mem = row.replace("<b>", "").replace("</b>", "")
#            print(date_mem)
        else:
            # Observation
            if row:
#                print(i, row)
                obs_list = split_observation(row)
                obs_list.append(date_mem)
                observations.append(obs_list)

    return observations


def append_or_add(dictionary, key):
    dictionary[key] = dictionary.get(key, 0) + 1


def get_stats_html(observations):
    species_counts = dict()

    for obs in observations:
        append_or_add(species_counts, obs[0])

    species_counts = sorted(species_counts.items(), key=lambda item: item[1], reverse=True)

    html = "<ul id='stats'>"

    i = 0
    limit = 10
    for species in species_counts:
        html += f"<li>{ species[0] }: { species[1] }</li>"
        i += 1
        if i >= limit:
            break

    html += "</ul>"

    return html


def get_location_report_html(observations, location):
    html = "<table id='location_report'>"

    i = 0
    limit = 10
    for obs in observations:
        if location in obs[1]:
            obs[1] = obs[1].replace(location, "").strip()
            html += f"<tr><td>{ obs[0] }</td><td>{ obs[5] }</td><td>{ obs[1][:20] }</td><td>{ obs[2] }</td><td>{ obs[3][:20] }</td><td>{ obs[4][:20] }</td></tr>\n"

            i += 1
            if i >= limit:
                break

    html += "</table>"

    return html



def main(secret):

    # Init and check secret
    html = dict()
    if secret != app_secrets.bird_secret:
        return html

    # Get and parse data
    html_content = fetch_html(app_secrets.bird_url, app_secrets.bird_class)
    observations = parse_html(html_content)

#    print(observations)

    html["stats"] = get_stats_html(observations)
    html["location_report"] = get_location_report_html(observations, "Espoo")

    return html
