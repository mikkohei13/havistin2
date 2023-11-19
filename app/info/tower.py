

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
    

def format_data(data):
    data2 = dict()
    for measurement in data:
        name = measurement["name"]

        measurement_dict = dict()
        heights_list = measurement["positions"].split(" ")
        measurements_list = measurement["doubleOrNilReasonTupleList"].split(" ")

        count = 0
        for height in heights_list:
            measurement_dict[str(int(float(height)))] = float(get_nth_value(measurements_list, count)) 
            count = count + 1

        data2[name] = measurement_dict

    return data2


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
    
    url = "http://opendata.fmi.fi/wfs?service=WFS&version=2.0.0&request=getFeature&storedquery_id=fmi::observations::weather::mast::multipointcoverage&fmisid=101000"

    data = extract_data_from_members(url)
    print(data)

    data2 = format_data(data)
    print(data2)

    html = dict()
    html["test"] = "Latokaski"
    html["test2"] = "Latokaski2"
    return html
