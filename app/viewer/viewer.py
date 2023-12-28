
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


# Todo: should handle lists of values, e.g. identificationBasis
def get_field(data, key, label):
        
    # Gets labels from schema. Is there a better way to do this?
    if key in data:
        # If value is URI, fetch label for it
        if "http://tun.fi" in data[key]:
            data_dict = common_helpers.fetch_finbif_api(data[key] + "?format=json&foo")
            value = data[key] # Use value as is as the default, in case translation is not found
            for labels in data_dict['label']:
                if "fi" == labels['@language']:
                    value = labels['@value']
                    break
        else:
            value = data[key]

        return f"<li>{ label }: { value }</li>\n"
    else:
        return ""


def get_multi_field(data, key, label):        
    if key in data:
        values = ", ".join(data[key])
        return f"<li>{ label }: { values }</li>\n"
    else:
        return ""


def get_facts(unit):
    if "facts" in unit:
        html = "<ul class='facts'>\n"
        for fact in unit['facts']:
            html += f"<li>{ fact['fact'] }: { fact['value'] }</li>\n"
        html += "</ul>\n"
        return html
    else:
        return "<!-- No facts -->\n"

def get_html(doc, my_doc):
    html = ""
    for gathering in doc["document"]["gatherings"]:
        html += f"<div class='v_gathering' id='{ gathering['gatheringId'] }'>\n"
        html += gathering['gatheringId']

        # If observations in this gathering
        if "units" in gathering:
            for unit in gathering['units']:
                html += f"<div class='v_unit' id='{ unit['unitId'] }'>\n"
                html += f"<h4>{ format_name(unit['linkings']['taxon']) }</h4>"
                html += "<ul>"
                html += f"<li>Havainnon id: { unit['unitId'] }</li>"
                html += get_field(unit, "abundanceString", "Määrä")
                html += get_field(unit, "notes", "Lisätiedot")
                html += get_field(unit, "atlasClass", "Pesimävarmuusluokka")
                html += get_field(unit, "atlasCode", "Pesimävarmuusindeksi")
                html += get_multi_field(unit, "keywords", "Avainsanat")
                html += get_field(unit, "superRecordBasis", "Havainnon ylätyyppi")
                html += get_field(unit, "recordBasis", "Havainnon tyyppi")
                html += get_field(unit, "taxonVerbatim", "Kirjattu taksoni sanatarkasti")
                html += get_field(unit, "identificationBasis", "Määritysperuste")
                html += get_field(unit, "reportedTaxonConfidence", "Havainnoijan arvioima luotettavuus")
                html += f"<li>Havainnon alkuperäinen määritys: { format_name(unit['linkings']['originalTaxon']) }</li>\n"
                html += f"<li>Havainnon laatuluokitus: { unit['interpretations']['reliability'] }</li>\n"
                html += "</ul>\n"
                html += get_facts(unit)
                html += "</div><!-- u ends -->\n"
        # If ZERO observations in this gathering
        else:
            html += f"<div class='v_no_unit'>\n"
            html += "<p>Pelkkä havaintoalue.</p>"
            html += "</div><!-- no_unit ends -->\n"

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
