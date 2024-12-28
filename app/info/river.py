
from helpers import common_helpers
import json

def main():
    html = dict()

    # Water levels from Espoonjoki from Syke's service
    url = "https://wwwi2.ymparisto.fi/i2/81/q8102800y/ajo.json"
    river_data = common_helpers.fetch_api(url)

    # Extract water levels
    whav_lst = river_data.get("whav", {}).get("lst", [])
    
    # Replace null values with 0
    cleaned_data = [val if val is not None else 0 for val in whav_lst]
#    print(cleaned_data)

    # Convert data into format that can be used with chart.js
    html["river_data"] = json.dumps(cleaned_data)

    return html
