
import taxa.common as common
import taxa.cache_db as cache_db
import time
import math


def get_inat_data(sci_name):
    taxon_data = common.fetch_api(f"https://api.inaturalist.org/v1/search?q={sci_name}&locale=fi&preferred_place_id=7020&per_page=10", True)
#    common.print_log(taxon_data)

    return taxon_data


def get_inat_author(attribution):
    pieces = attribution.split(",")
    author = pieces[0].replace("(c) ", "")
    return author


def generate_photos_data(qname, photo_count_toget):

    photo_count = 0
    disallowed = ["ARR", "http://tun.fi/MZ.intellectualRightsARR", None]

    photos_data = dict()
    photos_data['photos'] = []
    photos_data['time'] = int(time.time())

    # TODO: Add links to original data

    # 1) Species photos from Laji.fi
    url = f"https://api.laji.fi/v0/taxa/{qname}?lang=fi&langFallback=true&maxLevel=0&includeHidden=false&includeMedia=true&includeDescriptions=false&includeRedListEvaluations=false&sortOrder=taxonomic&access_token="
    species_data = common.fetch_finbif_api(url, False)

    scientific_name = species_data['scientificName']

    # for each photo
    if "multimedia" in species_data:
        for photo in species_data['multimedia']:
            if photo['licenseAbbreviation'] not in disallowed:
                new_photo = dict()
                new_photo['photo_type'] = "taxon_photo"

                new_photo['full_url'] = photo['fullURL']
                new_photo['thumbnail_url'] = photo['thumbnailURL']

                # TODO: Fix cases where captions contain html, e.g. birds / MX.37580
                if "caption" in photo:
                    new_photo['caption_plain'] = photo['caption']
                elif "taxonDescriptionCaption" in photo:
                    if "fi" in photo['taxonDescriptionCaption']:
                        new_photo['caption_plain'] = photo['taxonDescriptionCaption']['fi']
                    elif "en" in photo['taxonDescriptionCaption']:
                        new_photo['caption_plain'] = photo['taxonDescriptionCaption']['en']
                    elif "sv" in photo['taxonDescriptionCaption']:
                        new_photo['caption_plain'] = photo['taxonDescriptionCaption']['sv']
                
                if "caption_plain" not in new_photo:
                    new_photo['caption_plain'] = ""

                new_photo['caption_html'] = new_photo['caption_plain']

                if "author" in photo:
                    new_photo['author'] = photo['author']
                else:
                    new_photo['author'] = "(tuntematon)"

                new_photo['license_raw'] = photo['licenseAbbreviation']
                new_photo['license_abbreviation'] = common.cc_abbreviation(photo['licenseAbbreviation'])
                
                new_photo['attribution_plain'] = new_photo['author'] + ", " + new_photo['license_abbreviation'] + ", " + new_photo['caption_plain']

                # TODO: Add link to original URL, when it's available. Now it's sometimes in caption field.
                new_photo['source_url'] = "" # photo['document']['ORIGINAL_URL_FIELD']
            
                # Add the photo data dict the array of photos
                new_photo['rawdata'] = photo
                photos_data['photos'].append(new_photo)

                photo_count = photo_count + 1
                if photo_count >= photo_count_toget:
                    break
        
    if photo_count >= photo_count_toget:
        photos_data['photo_count'] = photo_count
        return photos_data

    # 2) Get expert verified observation photos
    species_data = common.fetch_finbif_api(f"https://api.laji.fi/v0/warehouse/query/unitMedia/list?taxonId={qname}&recordQuality=EXPERT_VERIFIED&aggregateBy=unit.linkings.taxon.id,media,document.documentId,unit.unitId&selected=unit.linkings.taxon.id,media,document.documentId,unit.unitId&includeNonValidTaxa=false&hasUnitMedia=true&cache=true&page=1&pageSize=4&access_token=", False)

    if species_data['total'] > 0:

        # For each photo
        # Limit verified photo count, since they are not necessarily good photos
        expert_verified_photo_count = math.floor(photo_count_toget / 3)
        i = 0

        for photo in species_data['results']:
            if "IMAGE" == photo['media']['mediaType']:
                if photo['media']['licenseId'] not in disallowed:
                    new_photo = dict()
                    new_photo['photo_type'] = "expert_verified"

                    new_photo['license_raw'] = photo['media']['licenseId']
                    new_photo['license_abbreviation'] = common.cc_abbreviation(photo['media']['licenseId'])
                    
                    new_photo['full_url'] = photo['media']['fullURL']
                    new_photo['thumbnail_url'] = photo['media']['thumbnailURL']

                    # TODO: Get author somehow (how?), or improve API to give this always
                    if "author" in photo['media']:
                        new_photo['author'] = photo['media']['author']
                    else:
                        new_photo['author'] = "(kuvaaja ei tiedossa)"
                    
                    new_photo['caption_plain'] = "Havainto/näyte " + photo['document']['documentId']
                    new_photo['caption_html'] = "Havainto/näyte <a href='" + photo['document']['documentId'] + "' target='_blank'>" + photo['document']['documentId'] + "</a>\n"

                    # Todo: Better differentiation from caption? How?
                    new_photo['attribution_plain'] = new_photo['author'] + ", " + new_photo['license_abbreviation'] + ", " + new_photo['caption_plain']

                    new_photo['source_url'] = photo['document']['documentId']

                    new_photo['rawdata'] = photo
                    photos_data['photos'].append(new_photo)

                    photo_count = photo_count + 1
                    if photo_count >= photo_count_toget:
                        break

                    i = i + 1
                    if i >= expert_verified_photo_count:
                        break

        if photo_count >= photo_count_toget:
            photos_data['photo_count'] = photo_count
            return photos_data

    # 3) Get iNat photos
    inat_data = get_inat_data(scientific_name)

    if inat_data['total_results'] >= 1:
        best_match = inat_data['results'][0]
        for photo in best_match['record']['taxon_photos']:
            if photo['photo']['license_code'] not in disallowed:
                new_photo = dict()
                new_photo['photo_type'] = "inat_taxon_photo"

                new_photo['license_raw'] = photo['photo']['license_code']
                new_photo['license_abbreviation'] = common.cc_abbreviation(photo['photo']['license_code'])
                
                new_photo['full_url'] = photo['photo']['original_url']
                new_photo['thumbnail_url'] = photo['photo']['small_url'] # or square_url ?

                new_photo['attribution_plain'] = photo['photo']['attribution']
                author = get_inat_author(photo['photo']['attribution'])
                new_photo['author'] = author
                new_photo['caption_plain'] = ""
                new_photo['caption_html'] = ""

                # TODO: If no native page url, get observation url. But that's on parent level -> need to change the whole loop.
                if "native_page_url" in photo['photo']:
                    new_photo['source_url'] = photo['photo']['native_page_url']

# Don't include raw data from iNat, because there's so much of it                
#                new_photo['rawdata'] = photo
                photos_data['photos'].append(new_photo)

                photo_count = photo_count + 1
                if photo_count >= photo_count_toget:
#                    common.print_log("Breaking at iNat photos, nro " + str(photo_count)) # debug
                    break

    # TODO: If adding specimen photos here later, you need to check on the 3) step if there are enough photos, and return results if yes.
    
    # If no more photos, return those that we do have
    photos_data['photo_count'] = photo_count
    return photos_data


def get_photos_data(qname, max_age_seconds, max_photo_count):
    # Note that changes to params (max_photo_count) & code will only take effect after cache has expired.

    # TODO: Make max photo count a param
    taxon_photos_db_collection = cache_db.connect_db()

    photos_data = cache_db.get_taxon_photos_data(taxon_photos_db_collection, qname)

    if not photos_data:
        # Get data and save to db
        photos_data = generate_photos_data(qname, max_photo_count)
        cache_db.set_taxon_photos_data(taxon_photos_db_collection, qname, photos_data)
        common.print_log("Created cache entry for " + qname)
    else:
        cache_age_seconds = int(time.time()) - photos_data['time']
        common.print_log("Cache age is " + str(cache_age_seconds) + " seconds")

        if cache_age_seconds > max_age_seconds:
            # Get fresh data and save to db
            photos_data = generate_photos_data(qname, max_photo_count)
            cache_db.set_taxon_photos_data(taxon_photos_db_collection, qname, photos_data)
            common.print_log("Regenerated cache for " + qname)
        else:
            # Use cached data
            common.print_log("Used cached data for " + qname)

    return photos_data


def main(qname_untrusted):
    # TODO: Return valid json with headers
    qname = common.valid_qname(qname_untrusted)

    html = dict()
    photos_data = get_photos_data(qname, 86400, 6)
        
    html['photos_data'] = photos_data
    return html
