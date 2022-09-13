
import taxa.common as common
import taxa.cache_db as cache_db
import time


def get_additional_photos(qname):
    photos = [] # list of dicts

    # Verified observations
    data = common.fetch_finbif_api(f"https://api.laji.fi/v0/warehouse/query/unitMedia/list?taxonId={qname}&reliability=RELIABLE&aggregateBy=unit.linkings.taxon.id,media,document.documentId,unit.unitId&selected=unit.linkings.taxon.id,media,document.documentId,unit.unitId&includeNonValidTaxa=false&hasUnitMedia=true&cache=true&page=1&pageSize=4&access_token=", False)

#    common.print_log("GETTING MORE IMAGES")
#    common.print_log(data)

    # If still no verified records, try specimens 
    if 0 == data['total']:
        data = common.fetch_finbif_api(f"https://api.laji.fi/v0/warehouse/query/unitMedia/list?taxonId={qname}&sourceId=KE.3&superRecordBasis=PRESERVED_SPECIMEN&aggregateBy=unit.linkings.taxon.id,media,document.documentId,unit.unitId&selected=unit.linkings.taxon.id,media,document.documentId,unit.unitId&includeNonValidTaxa=false&hasUnitMedia=true&cache=true&needsCheck=false&page=1&pageSize=4&access_token=", False)

    # If still no photos, return empty 
    if 0 == data['total']:
        return photos, False

    for item in data['results']:
        media = dict()
        if "IMAGE" == item['media']['mediaType']:
            media['licenseAbbreviation'] = item['media']['licenseId']
            media['fullURL'] = item['media']['fullURL']
            media['thumbnailURL'] = item['media']['thumbnailURL']
            media['author'] = item['media']['author']
            media['caption'] = "Havainto/näyte <a href='" + item['document']['documentId'] + "' target='_blank'>" + item['document']['documentId'] + "</a>\n"

            photos.append(media)

    return photos, True


def get_inat_data(sci_name):

    # Get taxon id
    # https://api.inaturalist.org/v1/search?q=seitsenpistepirkk&locale=fi&preferred_place_id=7020&per_page=10

    # API call on species page
    # https://api.inaturalist.org/v1/observations?verifiable=true&taxon_id=51702&place_id=&preferred_place_id=7020&locale=fi&order_by=observed_on&order=desc&per_page=1&skip_total_hits=true

    # API call on curation page
    # https://inaturalist.laji.fi/taxa/319877.json

    taxon_data = common.fetch_api(f"https://api.inaturalist.org/v1/search?q={sci_name}&locale=fi&preferred_place_id=7020&per_page=10", True)
    common.print_log(taxon_data)

    return taxon_data


def get_inat_author(attribution):
    pieces = attribution.split(",")
    author = pieces[0].replace("(c) ", "")
    return author


def generate_photos_data(qname, min_photo_count_toget):

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
                photo_count = photo_count + 1
                new_photo = dict()
                new_photo['photo_type'] = "taxon_photo"

                new_photo['full_url'] = photo['fullURL']
                new_photo['thumbnail_url'] = photo['thumbnailURL']

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
        
    if photo_count >= min_photo_count_toget:
        photos_data['photo_count'] = photo_count
        return photos_data

    # 2) Get expert verified observation photos
    species_data = common.fetch_finbif_api(f"https://api.laji.fi/v0/warehouse/query/unitMedia/list?taxonId={qname}&recordQuality=EXPERT_VERIFIED&aggregateBy=unit.linkings.taxon.id,media,document.documentId,unit.unitId&selected=unit.linkings.taxon.id,media,document.documentId,unit.unitId&includeNonValidTaxa=false&hasUnitMedia=true&cache=true&page=1&pageSize=4&access_token=", False)

    if species_data['total'] > 0:

        # for each photo (test)
        for photo in species_data['results']:
            if "IMAGE" == photo['media']['mediaType']:
                if photo['media']['licenseId'] not in disallowed:
                    photo_count = photo_count + 1
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

        if photo_count >= min_photo_count_toget:
            photos_data['photo_count'] = photo_count
            return photos_data

    # 3) Get iNat photos
    inat_data = get_inat_data(scientific_name)

    if inat_data['total_results'] >= 1:
        best_match = inat_data['results'][0]
        for photo in best_match['record']['taxon_photos']:
            if photo['photo']['license_code'] not in disallowed:
                photo_count = photo_count + 1
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

    # TODO: If adding specimen photos, you need to check on the 3) step if there are enough photos, and return results if yes.
    
    # If no more photos, return those that we do have
    photos_data['photo_count'] = photo_count
    return photos_data


def get_photos_data(qname, max_age_seconds):
    # TODO: Make max photo count a param
    taxon_photos_db_collection = cache_db.connect_db()

    photos_data = cache_db.get_taxon_photos_data(taxon_photos_db_collection, qname)

    if not photos_data:
        # Get data and save to db
        photos_data = generate_photos_data(qname, 6)
        cache_db.set_taxon_photos_data(taxon_photos_db_collection, qname, photos_data)
        common.print_log("Created cache entry for " + qname)
    else:
        cache_age_seconds = int(time.time()) - photos_data['time']
        common.print_log("Cache age is " + str(cache_age_seconds) + " seconds")

        if cache_age_seconds > max_age_seconds:
            # Get fresh data and save to db
            photos_data = generate_photos_data(qname, 6)
            cache_db.set_taxon_photos_data(taxon_photos_db_collection, qname, photos_data)
            common.print_log("Regenerated cache for " + qname)
        else:
            # Use cached data
            common.print_log("Used cached data for " + qname)

    return photos_data


def main():
    html = dict()
    html["foo"] = "bar"

    qname = "MX.229819" # keltasiimalude, lajikuvia
    qname = "MX.194380" # seitsenpistepirkko, varmistettuja havaintoja
    qname = "MX.1" # sudenkorennot
    qname = "MX.230504" # valtikkalude, lajikuvia iNatista
    qname = "MX.2"
    qname = "MX.229821"

    # Temp, get this when fetching images
#    taxon_data = common.fetch_finbif_api(f"https://api.laji.fi/v0/taxa/MX.194380?lang=fi&langFallback=true&maxLevel=0&includeHidden=false&includeMedia=false&includeDescriptions=false&includeRedListEvaluations=false&sortOrder=taxonomic&access_token=", False)
#    taxon_sci_name = taxon_data['scientificName']

#    get_inat_data(taxon_sci_name)

    photos_data = get_photos_data(qname, 600)
        
    html['raw'] = photos_data
    return html
