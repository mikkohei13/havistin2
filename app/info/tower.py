

from helpers import common_helpers

import requests

import xml.etree.ElementTree as ET


def extract_data_from_members(url):
    # Send a request to the URL and get the XML content
    response = requests.get(url)
    xml_content = response.content

    # Parse the XML content
    tree = ET.ElementTree(ET.fromstring(xml_content))
    root = tree.getroot()

    # Define the required namespaces
    namespaces = {
        'wfs': 'http://www.opengis.net/wfs/2.0',
        'swe': 'http://www.opengis.net/swe/2.0',
        'gml': 'http://www.opengis.net/gml/3.2',
        'gmlcov': 'http://www.opengis.net/gmlcov/1.0',
        # Add other namespaces as needed
    }

    # Loop through each 'wfs:member' element and extract the required data
    extracted_data = []
    for member in root.findall('.//wfs:member', namespaces):
        data = {}

        # Extract 'name' attribute of 'swe:field' element
        swe_field = member.find('.//swe:field', namespaces)
        if swe_field is not None:
            data['name'] = swe_field.attrib.get('name')

        # Extract value of 'gml:doubleOrNilReasonTupleList' element
        tuple_list = member.find('.//gml:doubleOrNilReasonTupleList', namespaces)
        if tuple_list is not None:
            data['doubleOrNilReasonTupleList'] = tuple_list.text.strip()

        # Extract value of 'gml:posList' element
        pos_list = member.find('.//gmlcov:positions', namespaces)
        if pos_list is not None:
            data['positions'] = pos_list.text.strip()

        extracted_data.append(data)

    return extracted_data


def get_nth_value(my_list, n):
    # Check if the index is within the range of the list
    if n >= 0 and n < len(my_list):
        return my_list[n]
    else:
        return "Index out of range"
    

# Formats data as key-value pairs
def format_data(data):
    data2 = dict()
    all_heights = set()

    for measurement in data:
        name = measurement["name"]

        measurement_dict = dict()

        heights_list = measurement["positions"].split(" ")
        measurements_list = measurement["doubleOrNilReasonTupleList"].split(" ")

        count = 0
        for height in heights_list:
            measurement_dict[str(int(float(height)))] = float(get_nth_value(measurements_list, count)) 
            all_heights.add(int(float(height)))
            count = count + 1

        data2[name] = measurement_dict

    all_heights = sorted(all_heights, reverse=True)
    return data2, all_heights


def measurement_html(data, height, measurement, suffix):
#    print("HERE:")
#    print(data)
#    print(measurement)

    # Get measurement or empty if missing
    meas = data[measurement].get(str(height), "")

    # Convert to integer if measurement is such that never has decimal accuracy
    if measurement == "RH" or measurement == "WD":
        if meas:
            meas = int(meas)
    if measurement == "WD":
        if meas:
            rotation = meas;
            meas = f"<img src='/static/arrow_white.png' alt='{ meas } deg' class='arrow' style='transform: rotate({ rotation }deg);'>"

    # Return html with content
    if meas:
        return f"<span class='meas_{ measurement }'><strong>{ meas }</strong> { suffix }</span>"
    # Return html without content
    else:
        return f"<span class='meas_{ measurement }'>&nbsp;</span>"


def windchill(data, height):
    temp = data["TA"].get(str(height), "")
    wind = data["WS"].get(str(height), "")

    if not temp:
        return "<span class='meas_wct'>&nbsp;</span>"
    if not wind:
        return "<span class='meas_wct'>&nbsp;</span>"

    # FMI formula: https://fi.wikipedia.org/wiki/Pakkasen_purevuus
    wct = 13.12 + 0.6215 * temp - 13.956 * wind ** 0.16 + 0.4867 * temp * wind ** 0.16

    # Canadian formula: https://en.wikipedia.org/wiki/Wind_chill
#    wct = 13.12 + 0.6215 * temp - 11.37 * wind ** 0.16 + 0.3965 * temp * wind ** 0.16

    wct = round(wct, 1)

    return f"<span class='meas_wct'>wct <strong>{ wct }</strong> &deg;C</span>"


def main():

    '''
    Stored queries:
    https://opendata.fmi.fi/wfs?service=WFS&version=2.0.0&request=describeStoredQueries&

    Tapiola data:
    http://opendata.fmi.fi/wfs?service=WFS&version=2.0.0&request=getFeature&storedquery_id=fmi::observations::weather::daily::timevaluepair&place=tapiola&

    Espoo masto:
    http://opendata.fmi.fi/wfs?service=WFS&version=2.0.0&request=getFeature&storedquery_id=fmi::observations::weather::mast::multipointcoverage&fmisid=101000

    Mittaukset:
    https://www.ilmatieteenlaitos.fi/avoin-data-mastohavainnot

    '''
    html = dict()
    
    url = "http://opendata.fmi.fi/wfs?service=WFS&version=2.0.0&request=getFeature&storedquery_id=fmi::observations::weather::mast::multipointcoverage&fmisid=101000"

    data = extract_data_from_members(url)

    data2, all_heights = format_data(data)
    print(data2)
    print(all_heights)

    stations = "<!-- Weather stations, i.e. height levels on the tower -->"
    for height in all_heights:
        station_html = ""

        height_str = str(int(float(height)))

        ta = measurement_html(data2, height, "TA", "&deg;C")
        ws = measurement_html(data2, height, "WS", "m/s")
        wd = measurement_html(data2, height, "WD", "")
        wg = measurement_html(data2, height, "WG", "puuska") # Gust 10 min
        rh = measurement_html(data2, height, "RH", "%")
        td = measurement_html(data2, height, "TD", "kaste") # Dew point
        wct = windchill(data2, height)

        top = 327 - int(float(height))
 
        station_html += f"\n<div class='station' id='station_{ height }' style='top: { top }px'>\n"
        station_html += f"<span class='meas_height'><strong>{ height_str }</strong></span> { ta } { wct } { ws } { wd } { wg } { rh } { td }"
        station_html += "\n</div>\n"

        stations += station_html

    html["test"] = "Latokaski"
    html["test2"] = stations
    return html

'''

{
   "TA":{
      "2":0.2,
      "26":1.2,
      "49":1.1,
      "92":0.9,
      "141":0.6,
      "217":-0.3,
      "265":-0.6,
      "297":-0.9
   },
   "RH":{
      "2":98.0,
      "26":87.0,
      "49":87.0,
      "92":87.0,
      "141":88.0,
      "217":93.0,
      "265":92.0,
      "297":94.0
   },
   "TD":{
      "2":-0.1,
      "26":-0.6,
      "49":-0.8,
      "92":-1.0,
      "141":-1.2,
      "217":-1.3,
      "265":-1.7,
      "297":-1.7
   },
   "WS":{
      "26":0.7,
      "92":1.9,
      "217":2.8,
      "327":5.2
   },
   "WD":{
      "26":243.0,
      "92":245.0,
      "217":233.0,
      "327":236.0
   },
   "WG":{
      "26":1.2,
      "92":2.0,
      "217":3.8,
      "327":6.4
   }
}

'''