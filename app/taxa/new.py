import json
#from webbrowser import get
import taxa.common as common

# Here is manually defined which species are "new", this depends on existing literature of that taxon.
def get_species_qnames(qname):
    species = list()
    if "MX.229577" == qname:
        
        species.append("MX.5075811")
        species.append("MX.229664")
        #species.append("MX.230068") # debug duplicate
        #species.append("MX.4994296") # debug duplicate
        #species.append("MX.230504") # debug duplicate
        
        species.append("MX.4999057")
        species.append("MX.5080747")
        species.append("MX.5074723")
        species.append("MX.4994279")
        species.append("MX.5074543")
        species.append("MX.229795")
        species.append("MX.229799")
        species.append("MX.229791")
        species.append("MX.229815")
        species.append("MX.229816")
        species.append("MX.229819")
        species.append("MX.4994280")
        species.append("MX.229829")
        species.append("MX.5008074")
        species.append("MX.5080746")
        species.append("MX.5018544")
        species.append("MX.4994281")
        species.append("MX.4994283")
        species.append("MX.229973")
        species.append("MX.5080726")
        species.append("MX.4994291")
        species.append("MX.4994284")
        species.append("MX.4994285")
        species.append("MX.4994286")
        species.append("MX.230068")
        species.append("MX.4994287")
        species.append("MX.230095")
        species.append("MX.4994288")
        species.append("MX.4994289")
        species.append("MX.4994292")
        species.append("MX.230173")
        species.append("MX.5082045")
        species.append("MX.230230")
        species.append("MX.4994293")
        species.append("MX.5075004")
        species.append("MX.5077007")
        species.append("MX.5016606")
        species.append("MX.230303")
        species.append("MX.230415")
        species.append("MX.5008073")
        species.append("MX.230504")
        species.append("MX.4994295")
        species.append("MX.4994296")
        species.append("MX.230542")
        species.append("MX.5015646")
        species.append("MX.230548")
        species.append("MX.230556")
        
    return species

def get_species_data(species_qnames):
    species_data = []
    for qname in species_qnames:
        data = common.fetch_finbif_api(f"https://api.laji.fi/v0/taxa/{qname}?lang=fi&langFallback=true&maxLevel=0&includeHidden=true&includeMedia=true&includeDescriptions=true&includeRedListEvaluations=false&sortOrder=taxonomic&access_token=")
#        common.print_log(data) # debug
        species_data.append(data)

    return species_data


def get_additional_multimedia(qname):
    multimedia = [] # list of dicts

    # Verified observations
    data = common.fetch_finbif_api(f"https://api.laji.fi/v0/warehouse/query/unitMedia/list?taxonId={qname}&reliability=RELIABLE&aggregateBy=unit.linkings.taxon.id,media,document.documentId,unit.unitId&selected=unit.linkings.taxon.id,media,document.documentId,unit.unitId&includeNonValidTaxa=false&hasUnitMedia=true&cache=true&page=1&pageSize=4&access_token=")

#    common.print_log("GETTING MORE IMAGES")
#    common.print_log(data)

    # If still no verified records, try specimens 
    if 0 == data['total']:
        data = common.fetch_finbif_api(f"https://api.laji.fi/v0/warehouse/query/unitMedia/list?taxonId={qname}&sourceId=KE.3&superRecordBasis=PRESERVED_SPECIMEN&aggregateBy=unit.linkings.taxon.id,media,document.documentId,unit.unitId&selected=unit.linkings.taxon.id,media,document.documentId,unit.unitId&includeNonValidTaxa=false&hasUnitMedia=true&cache=true&needsCheck=false&page=1&pageSize=4&access_token=")

    # If still no photos, return empty 
    if 0 == data['total']:
        return multimedia, False

    for item in data['results']:
        media = dict()
        if "IMAGE" == item['media']['mediaType']:
            # TODO: harmonize cc-links to abbreviation
            media['licenseAbbreviation'] = item['media']['licenseId']
            media['fullURL'] = item['media']['fullURL']
            media['thumbnailURL'] = item['media']['thumbnailURL']
            media['author'] = item['media']['author']
            media['caption'] = "Havainto/näyte " + item['document']['documentId']

            multimedia.append(media)

    return multimedia, True


def generate_media_html(media_data, qname):

    disallowed = ["ARR", "http://tun.fi/MZ.intellectualRightsARR"]

    html = ""
    for media in media_data:
        if media['licenseAbbreviation'] not in disallowed:
            html += "\n<figure class='photo'>\n"
            html += "<a href='" + media['fullURL'] + "'><img src='" + media['thumbnailURL'] + "' alt='' title=''></a>"
            html += "<figcaption>\n"
            if "caption" in media:
                html += "<span class='caption'>" + media['caption'] + "</span><br>\n"
            html += "<span class='copyright'>" + media['author'] + ", " + media['licenseAbbreviation'] + "</span>"
            html += "</figcaption>\n"
            html += "</figure>\n"
        else:
            html += "<!-- non-cc media -->\n"

    return html

def generate_species_html(species_data):
    html = ""

    family_mem = ""

    for species in species_data:
        qname = species['qname']
        family = species['parent']['family']['scientificName']

        if family != family_mem:
            html += f"<h2 class='new_family'>{family}</h2>"
            family_mem = family

        html += "\n<div class='species'>\n"
        if "vernacularName" in species:
            vernacular_name = species['vernacularName'].capitalize()
            html += f"<h3><em>{vernacular_name}</em> - {species['scientificName']} {species['scientificNameAuthorship']}</h3>\n"
        else:
            html += f"<h3><em>{species['scientificName']}</em> {species['scientificNameAuthorship']}</h3>\n"

        html += "<ul class='speciesinfo'>\n"

        # TODO: Can there be multiple statuses? Yes.
        if "typeOfOccurrenceInFinland" in species:
            html += "<li>"
            for status in species['typeOfOccurrenceInFinland']:
                translated_status = common.map_status(status)
                html += f"{translated_status}, "
        else:
            html += "<li>ei statustietoa"

        html += " <a href='/taxa/species/" + qname + "'>lisätietoa &raquo;</a></li>\n"
        
        html += "<li>Laji.fi:ssa <a href='https://laji.fi/observation/map?target=" + qname + "&countryId=ML.206&recordQuality=EXPERT_VERIFIED,COMMUNITY_VERIFIED,NEUTRAL&needsCheck=false'>" + str(species['observationCountFinland']) + " havaintoa Suomesta</a>, <a href='https://laji.fi/taxon/" + qname + "'>lajisivu</a></li>\n"

        html += "</ul>\n"

        # Photos
        # If no taxon photos, try different sources
        if "multimedia" not in species:
            species['multimedia'], got_images = get_additional_multimedia(qname)
            species['hasMultimedia'] = got_images

        # Create photo html
        html += "<div class='multimedia'>\n"
        if True == species['hasMultimedia']:
            html += generate_media_html(species['multimedia'], species['qname'])
        else:
            html += "ei kuvia"
        html += "</div>\n"

#        html += json.dumps(species) # debug
        html += "</div>\n"

    return html


def main(taxon_id_untrusted):

    qname = common.valid_qname(taxon_id_untrusted)

    html = dict()

    species_qnames = get_species_qnames(qname)
    
    species_data = get_species_data(species_qnames)

    html["species_html"] = generate_species_html(species_data)

    taxon_data = common.fetch_finbif_api(f"https://api.laji.fi/v0/taxa/{qname}?lang=fi&langFallback=true&maxLevel=0&includeHidden=false&includeMedia=false&includeDescriptions=false&includeRedListEvaluations=false&sortOrder=taxonomic&access_token=")

    html["vernacular_name"] = taxon_data["vernacularName"]
    html["scientific_name"] = taxon_data["scientificName"]

    return html
