
from helpers import common_helpers
import datetime
import json
import re

def validate_document_qname(document_id_untrusted):
    pattern = re.compile(r'^[a-zA-Z0-9\-._:/\\]+$') # Full URI
    if re.match(pattern, document_id_untrusted):
        return document_id_untrusted
    else:
        return False


def get_single_doc(document_id, token):
    url = f"https://api.laji.fi/v0/warehouse/query/document?documentId={ document_id }&editorOrObserverPersonToken={ token }&access_token="
    data_dict = common_helpers.fetch_finbif_api(url)
    my_document = True

    if 404 == data_dict.get("status", 0):
        print("here")
        url = f"https://api.laji.fi/v0/warehouse/query/document?documentId={ document_id }&access_token="
        data_dict = common_helpers.fetch_finbif_api(url)
        my_document = False

    return data_dict, my_document


def format_name(unit):
    prefix = ""
    suffix = ""
    if unit["cursiveName"]:
        prefix = "<em>"
        suffix = "</em>"

    if "nameFinnish" in unit:
        return f"{ unit['nameFinnish']} ({ prefix }{ unit['scientificName']}{ suffix } { unit['scientificNameAuthorship'] })"
    else:
        return f"{ prefix }{ unit['scientificName']}{ suffix } { unit['scientificNameAuthorship'] }"


def get_html(doc, my_doc):
    html = ""
    for gathering in doc["document"]["gatherings"]:
        html += f"<div class='v_gathering' id='{ gathering['gatheringId'] }'>\n"
        html += gathering['gatheringId']

        for unit in gathering['units']:
            html += f"<div class='v_unit' id='{ unit['unitId'] }'>\n"
            html += unit['unitId']
            html += f"<h4>{ format_name(unit['linkings']['taxon']) }</h4>"
            html += "</div><!-- u ends -->\n"


        html += "</div><!-- g ends -->\n"

    return html


def main(token, document_id_untrusted):

    '''
    Kotka Turku Oribatida: http://mus.utu.fi/ZMUT.24776-ORI
    Oma Vihko trip: http://tun.fi/JX.1660642
    Oma iNat korjattu: http://tun.fi/HR.3211/125754936
    Varmistettu, Hannan: http://tun.fi/JX.1607740

    '''

    # --------------------
    # Prepare

    document_id = validate_document_qname(document_id_untrusted)
    if not document_id:
        raise Exception

    html = dict()

    # --------------------
    # Get data

    doc, my_doc = get_single_doc(document_id, token)

    html["data"] = doc

    html["doc"] = get_html(doc, my_doc)

    return html
