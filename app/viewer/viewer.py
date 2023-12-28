
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
        return f"{ unit['nameFinnish']} ({ prefix }{ unit['scientificName']}{ suffix } { unit.get('scientificNameAuthorship', '') })"
    else:
        return f"{ prefix }{ unit['scientificName']}{ suffix } { unit.get('scientificNameAuthorship', '') }"


def format_shortname(unit):

    if "nameFinnish" in unit:
        return f"{ unit['nameFinnish']}"
    else:
        prefix = ""
        suffix = ""
        if unit["cursiveName"]:
            prefix = "<em>"
            suffix = "</em>"
        return f"{ prefix }{ unit['scientificName']}{ suffix }"


# Todo: should handle lists of values, e.g. identificationBasis
def get_field(data, key, label):
        
    # Gets labels from schema. Is there a better way to do this?
    if key in data:
        # If value is URI, fetch label for it
        if "http://tun.fi" in str(data[key]):
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
        html = "<ul class='v_unit_facts'>\n"
        for fact in unit['facts']:
            html += f"<li>{ fact['fact'] }: { fact['value'] }</li>\n"
        html += "</ul>\n"
        return html
    else:
        return "<!-- No facts -->\n"


def get_collection(collection_id):
    collection_id = collection_id.replace("http://tun.fi/", "")
    url = f"https://api.laji.fi/v0/collections/{ collection_id }?langFallback=true&access_token="
    data_dict = common_helpers.fetch_finbif_api(url)
    return data_dict


def get_collection_quality_symbol(collection_quality_qname):
    if collection_quality_qname:
        if "MY.collectionQualityEnum1" == collection_quality_qname:
            return "<img id='v_collection_quality_symbol' src='https://laji.fi/static/images/quality-icons/collection/amateur_collection.svg'>"
        if "MY.collectionQualityEnum2" == collection_quality_qname:
            return "<img id='v_collection_quality_symbol' src='https://laji.fi/static/images/quality-icons/collection/hobbyist_collection.svg'>"
        if "MY.collectionQualityEnum3" == collection_quality_qname:
            return "<img id='v_collection_quality_symbol' src='https://laji.fi/static/images/quality-icons/collection/professional_collection.svg'>"
    else:
        return ""


def get_unit_quality_symbol(unit_quality_qname):
    if unit_quality_qname:
        if "EXPERT_VERIFIED" == unit_quality_qname:
            return "<img id='v_unit_quality_symbol' src='https://laji.fi/static/images/quality-icons/record/expert_verified.svg'>"
        if "COMMUNITY_VERIFIED" == unit_quality_qname:
            return "<img id='v_unit_quality_symbol' src='https://laji.fi/static/images/quality-icons/record/community_verified.svg'>"
        if "NEUTRAL" == unit_quality_qname:
            return "<img id='v_unit_quality_symbol' src='https://laji.fi/static/images/quality-icons/record/neutral.svg'>"
        if "UNCERTAIN" == unit_quality_qname:
            return "<img id='v_unit_quality_symbol' src='https://laji.fi/static/images/quality-icons/record/uncertain.svg'>"
        if "ERRONEOUS" == unit_quality_qname:
            return "<img id='v_unit_quality_symbol' src='https://laji.fi/static/images/quality-icons/record/erroneous.svg'>"
    else:
        return "PUUTTUU"


def hashify(s):
    s = s.replace("/", "_")
    s = s.replace(":", "_")
    s = s.replace(".", "_")
    s = s.replace("#", "_")
    return s


def get_sidebar(doc):
    html = "<div id='v_sidebar'>\n"
    html += f"<ul>\n"    
    for gathering in doc["document"]["gatherings"]:
        html += f"<li data-target='{ hashify(gathering['gatheringId']) }'>\n"
        if "units" in gathering:
            for unit in gathering['units']:
                html += f"{ format_shortname(unit['linkings']['taxon']) }<br>\n"
        else:
            html += "Ei havaintoja\n"
        html += "</li>\n"
    html += "</ul>\n"
    html += "</div>\n<!-- v_sidebar ends -->\n"
    return html


def get_html(doc, my_doc):
    collection_data = get_collection(doc['document']['collectionId'])
    html = ""

    html += "<div id='v_document_head'>\n"
    html += f"<h1>{ doc['document']['documentId'] } <span class='v_button' onclick=\"copyToClipboard('{ doc['document']['documentId'] }')\">Kopioi</span></h1>\n"

    if my_doc:
        html += "<span id='v_my_document'>🙋 Oma havaintosi</span>"
        html += f"<a class='v_button' id='v_edit' href='#'>✏ Muokkaa</a>"

    html += "<ul>\n"
    html += f"<li>Lähdeaineisto: <a href='{ doc['document']['collectionId'] }'>{ collection_data['collectionName'] }</a> &ndash; { doc['document']['collectionId'] } <span class='v_info' title='{ collection_data.get('description', 'Aineistolla ei ole kuvausta.') }'>🔍</span></li>\n"
    if "referenceURL" in doc['document']:
        html += f"<ul><li><a href='{ doc['document']['referenceURL'] }' target='_blank'>Lisää tietoa alkuperäislähteessä</a></li></ul>\n"

    html += f"<li>Aineiston luokitus: { get_collection_quality_symbol(collection_data.get('collectionQuality', '')) } { collection_data.get('collectionQuality', '') } <span class='v_info' title='{ collection_data.get('dataQualityDescription', 'Aineiston laadusta ei ole lisätietoja.') }'>🔍</span></li>\n"

    html += get_multi_field(doc['document'], 'keywords', 'Avainsanat')
    html += "</ul>\n"
    html += "<ul>\n"
    html += get_field(doc['document'], "created", "Luotu")
    html += get_field(doc['document'], "firstLoadDate", "Ladattu Lajitietokeskukseen")
    html += get_field(doc['document'], "loadDate", "Muokattu") # Check that terms are correct
    html += get_field(doc['document']['linkings']['editors'][0], "fullName", "Muokkaaja")
    html += "</ul>\n"

    html += "</div><!-- v_document_head ends -->\n"

    html += "<div id='v_maincontent'>\n"

    # Sidebar
    html += get_sidebar(doc)

    # Content elements
    html += "<div id='v_content'>"
    first_class = " active-tab"

    # ---------------------------------------
    # Gatherings
    for gathering in doc["document"]["gatherings"]:
        html += f"<div class='v_gathering{ first_class }' id='{ hashify(gathering['gatheringId']) }'>\n"
        first_class = ""

        html += "<ul>\n"
        html += f"<li>Keruutapahtuman tunniste: { gathering['gatheringId'] }</li>\n"
        html += f"<li>Aika: { gathering['displayDateTime'] }</li>\n"
        html += f"<li>Maa: { gathering['interpretations']['countryDisplayname'] }</li>\n"
        html += f"<li>Eliömaakunta: { gathering['interpretations']['biogeographicalProvinceDisplayname'] }</li>\n"
        html += f"<li>Kunta: { gathering['interpretations']['municipalityDisplayname'] }</li>\n"
        html += f"<li>Paikka: { gathering.get('locality', '') }</li>\n"
        html += f"<li>Lisätietoja: { gathering.get('notes', '') }</li>\n"
        html += f"<li>Havainnoijat: { ', '.join(gathering['team']) }</li>\n"
        html += "</ul>\n"

        # If observations in this gathering
        if "units" in gathering:
            # ---------------------------------------
            # Units
            for unit in gathering['units']:

                html += f"<div class='v_unit' id='{ unit['unitId'] }'>\n"
                html += f"<h4>{ format_name(unit['linkings']['taxon']) }</h4>"
                html += "<ul class='v_unit_basic'>"
                html += f"<li>Havainnon tunniste: { unit['unitId'] }</li>"
                html += get_field(unit, "abundanceString", "Määrä")
                html += get_field(unit, "notes", "Lisätiedot")
                html += get_field(unit, "atlasClass", "Pesimävarmuusluokka")
                html += get_field(unit, "atlasCode", "Pesimävarmuusindeksi")
                html += get_field(unit, "externalMediaCount", "Mediatiedostoja alkuperäislähteessä")
                html += f"<li>Havainnon laatuluokitus: { get_unit_quality_symbol(unit['interpretations']['recordQuality']) } { unit['interpretations']['recordQuality'] }</li>\n"

                html += "</ul>"
                html += "<ul class='v_unit_advanced'>"
                html += get_multi_field(unit, "keywords", "Avainsanat")
                html += get_field(unit, "superRecordBasis", "Havainnon ylätyyppi")
                html += get_field(unit, "recordBasis", "Havainnon tyyppi")
                html += get_field(unit, "taxonVerbatim", "Kirjattu taksoni sanatarkasti")
#                html += get_field(unit, "identificationBasis", "Määritysperuste") # Can contain multiple values
                html += get_field(unit, "reportedTaxonConfidence", "Havainnoijan arvioima luotettavuus")
                html += f"<li>Havainnon alkuperäinen määritys: { format_name(unit['linkings']['originalTaxon']) }</li>\n"
                html += "</ul>\n"
                html += get_facts(unit)
                html += "</div><!-- unit ends -->\n"
        # If ZERO observations in this gathering
        else:
            html += f"<div class='v_no_unit'>\n"
            html += "<p>Pelkkä havaintoalue.</p>"
            html += "</div><!-- no_unit ends -->\n"

        html += "</div><!-- v_gatherging ends -->\n"
    html += "</div><!-- v_content ends -->\n"
    html += "</div><!-- v_maincontent ends -->\n"

    return html



def main(token, document_id_untrusted):

    '''
    Kotka Turku Oribatida: http://mus.utu.fi/ZMUT.24776-ORI
    Oma Vihko trip: http://tun.fi/JX.1660642
    Oma närhi: http://tun.fi/JX.1661784
    Oma iNat korjattu: http://tun.fi/HR.3211/125754936
    Varmistettu, Hannan: http://tun.fi/JX.1607740
    Oma talvilintu: http://tun.fi/JX.1516575

    Note:
    - fragment linking works on trip form gathering id's but not unit id's.

    Major todo's:
    - unit and gathering images, habitat vs. species images
    - map
    - coordinates, includion geometries and errors

    '''

    # --------------------
    # Prepare

    document_id = validate_document_qname(document_id_untrusted)
    if not document_id:
        raise Exception

    html = dict()
    html['document_id'] = document_id

    # --------------------
    # Get data

    doc, my_doc = get_single_doc(document_id, token)

    html["data"] = doc

    html["doc"] = get_html(doc, my_doc)

    return html
