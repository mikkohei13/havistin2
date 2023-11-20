

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


def main(secret):

    # Init and check secret
    html = dict()
    if secret != app_secrets.bird_secret:
        return html

    # Get data
    html_content = fetch_html(app_secrets.bird_url, app_secrets.bird_class)

    print(html_content)

#    html_content = html_content.replace("<br/><br/>", "")
    rows = html_content.split("<br/>")

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
            print(date_mem)
        else:
            # Observation
            if row:
#                print(i, row)
                obs_list = split_observation(row)
                obs_list.append(date_mem)
                print(obs_list)


    '''
    # Split the HTML content into entries
    entries = re.split(r'<br/>\s*<b>\d+\.\d+\.</b><br/>', html_parts[0])

    # Filter out empty strings and parse each entry
    parsed_data = [parse_entry(entry) for entry in entries if entry.strip()]
    print(parsed_data)
    '''

    html["test"] = html_content
    return html
