

from helpers import common_helpers
import app_secrets

import requests
from bs4 import BeautifulSoup


def fetch_and_parse_table(url, class_name):
    # Fetch HTML content from the URL
    response = requests.get(url)
    html_content = response.text

    # Parse HTML using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the div with class 'foo' and then find the table within this div
    div = soup.find('div', {'class': class_name})

    tables = div.find_all('table') if div else []
    nested_table = tables[1] if len(tables) > 1 else None  # Assuming the nested table is the second one


    # Extract each row into a list
    rows_list = []
    for tr in nested_table.find_all('tr'):
        cells = tr.find_all('td')
        row_data = [cell.text for cell in cells]
        rows_list.append(row_data)

    return rows_list


def main(secret):

    # Init and check secret
    html = dict()
    if secret != app_secrets.bird_secret:
        return html

    # Get data
    obs_dict = fetch_and_parse_table(app_secrets.bird_url, app_secrets.bird_class)
    print(obs_dict)


    html["test"] = "Ok!"
    return html
