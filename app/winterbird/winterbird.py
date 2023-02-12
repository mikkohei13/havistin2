

from datetime import timedelta, date
#import json

from helpers import common_helpers
import app_secrets


def get_photo_html(photo):

    license_html = common_helpers.cc_abbreviation(photo.get('licenseId', '(ei lisenssiä)'))

    photo_html = ""
    photo_html += "<div class='winterbird_photo'>\n"
    photo_html += f"<img src='{photo['fullURL']}'>\n"
#                photo_html += f"<img src='{photo['thumbnailURL']}'>\n"
    photo_html += f"<p>{photo.get('caption', '(ei kuvatekstiä)')} - {photo.get('copyrightOwner', '(ei kuvaajan nimeä)')} - {license_html}</p>\n"
    photo_html += "</div>\n"

    return photo_html


def get_habitat_photos(collection_id, dev_secret = 1):
    # displayDateTime vs. eventDate.begin ?

    shown_documents = []

    dev_mode = False
    if dev_secret == app_secrets.dev_secret:
        print("NOTICE: Dev mode on")
        dev_mode = True

    # Documents with photos:
    # DESC = newest first
    page_size = 200
#    page_size = 10 # debug
    page = 1
    api_url = f"https://api.laji.fi/v0/warehouse/query/gathering/aggregate?aggregateBy=gathering.conversions.wgs84CenterPoint.lat%2Cgathering.conversions.wgs84CenterPoint.lon%2Cdocument.documentId%2Cgathering.displayDateTime&orderBy=gathering.displayDateTime DESC&onlyCount=true&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize={page_size}&page={page}&cache=true&collectionId={collection_id}&hasGatheringMedia=true&access_token="

    documents_dict = common_helpers.fetch_finbif_api(api_url)

    photo_html = ""

    # Each document
    for document in documents_dict["results"]:
        document_id = document["aggregateBy"]["document.documentId"]
        lat = round(float(document["aggregateBy"]["gathering.conversions.wgs84CenterPoint.lat"]))
        lon = round(float(document["aggregateBy"]["gathering.conversions.wgs84CenterPoint.lon"]))

        map_filename = f"/static/maps/{ lat }_{ lon }.png"

        # Skip documents that have already been shown
        if document_id in shown_documents:
            print(f"WARNING: Skipping duplicate document {document_id}")
            continue

        api_url = f"https://api.laji.fi/v0/warehouse/query/single?documentId={ document_id }&cache=true&access_token="
        document_dict = common_helpers.fetch_finbif_api(api_url)
#        print(document_dict)

        # Check to be sure that there are photos
        if "media" in document_dict["document"]["gatherings"][0]:

            photo_count = len(document_dict["document"]["gatherings"][0]["media"])

            # Data about the gathering
            photo_html += f"<div class='winterbird_document'>"
            date = document_dict["document"]["gatherings"][0].get('displayDateTime', '(ei päivämäärää)')
            locality = document_dict["document"]["gatherings"][0].get('locality', '(ei paikannimeä)')

            if "units" in document_dict["document"]["gatherings"][0]:
                taxa_count = len(document_dict["document"]["gatherings"][0]["units"])
            else:
                taxa_count = 0

            photo_html += f"<h3>{ locality } - { date }</h3>\n"
            photo_html += f"<p><img src='{ map_filename }' class='minimap' alt=''><a href='{ document_id }'>{ document_id }</a> - { taxa_count } havainto(a), { photo_count } habitaattikuva(a)</p>\n"

            photo_html += "<div class='route-photos'>"
            # Each photo
#            common_helpers.print_log(document_dict["document"]["gatherings"][0]["media"]) # debug
            media = document_dict["document"]["gatherings"][0]["media"]
            for photo in media:
                if photo.get('licenseId', 'http://tun.fi/MZ.intellectualRightsARR') == "http://tun.fi/MZ.intellectualRightsARR" and dev_mode == False:
                    photo_html += "<span class='no_cc_license'>(kuva ilman CC-lisenssiä)</span> "
                else:
                    photo_html += get_photo_html(photo)

            photo_html += "</div>\n</div>\n\n"
        
        else:
            print(f"WARNING: No media in document {document_id}")

        shown_documents.append(document_id)

    return photo_html



def main(dev_secret_dirty):
    dev_secret = int(dev_secret_dirty)

    html = dict()

    # TODO: Paging

    html["photo_html"] = get_habitat_photos("HR.39", dev_secret)

    return html
