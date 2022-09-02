import json
#from webbrowser import get
import taxa.common as common

# Here is manually defined which species are "new", this depends on existing literature of that taxon.
def get_species_qnames(page_name_untrusted):
    species = list()
    taxon_qname = ""

    if "heteroptera_new" == page_name_untrusted:
        taxon_qname = "MX.229577"

        '''
        species.append("MX.5075811") # debug duplicate
        species.append("MX.229664") # debug duplicate
        species.append("MX.230068") # debug duplicate
        species.append("MX.229819") # debug duplicate
        species.append("MX.229815") # debug duplicate
        species.append("MX.4994296") # debug duplicate
        species.append("MX.230542") # debug duplicate
        species.append("MX.230504") # debug duplicate
        '''
        species.append("MX.5075811")
        species.append("MX.229664")
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
        
    return taxon_qname, species

def get_species_data(species_qnames):
    species_data = []
    for qname in species_qnames:
        data = common.fetch_finbif_api(f"https://api.laji.fi/v0/taxa/{qname}?lang=fi&langFallback=true&maxLevel=0&includeHidden=true&includeMedia=true&includeDescriptions=true&includeRedListEvaluations=false&sortOrder=taxonomic&access_token=", False)
#        common.print_log(data) # debug
        species_data.append(data)

    return species_data


def cc_link(lic):
    if "http://tun.fi/MZ.intellectualRightsCC-BY-NC-4.0" == lic or "CC-BY-NC-4.0" == lic:
        return "CC BY-NC 4.0"
    if "http://tun.fi/MZ.intellectualRightsCC-BY-SA-4.0" == lic or "CC-BY-SA-4.0" == lic:
        return "CC BY-SA 4.0"
    if "http://tun.fi/MZ.intellectualRightsCC-BY-4.0" == lic or "CC-BY-4.0" == lic:
        return "CC BY 4.0"
    if "http://tun.fi/MZ.intellectualRightsCC-BY-NC-ND-4.0" == lic or "CC-BY-NC-ND-4.0" == lic:
        return "CC BY-NC-ND 4.0"
    if "http://tun.fi/MZ.intellectualRightsCC-BY-NC-SA-4.0" == lic or "CC-BY-NC-SA-4.0" == lic:
        return "CC BY-NC-SA 4.0"
#    if "" == lic or "" == lic:
#        return ""
    return lic


def get_additional_multimedia(qname):
    multimedia = [] # list of dicts

    # Verified observations
    data = common.fetch_finbif_api(f"https://api.laji.fi/v0/warehouse/query/unitMedia/list?taxonId={qname}&reliability=RELIABLE&aggregateBy=unit.linkings.taxon.id,media,document.documentId,unit.unitId&selected=unit.linkings.taxon.id,media,document.documentId,unit.unitId&includeNonValidTaxa=false&hasUnitMedia=true&cache=true&page=1&pageSize=4&access_token=", False)

#    common.print_log("GETTING MORE IMAGES")
#    common.print_log(data)

    # If still no verified records, try specimens 
    if 0 == data['total']:
        data = common.fetch_finbif_api(f"https://api.laji.fi/v0/warehouse/query/unitMedia/list?taxonId={qname}&sourceId=KE.3&superRecordBasis=PRESERVED_SPECIMEN&aggregateBy=unit.linkings.taxon.id,media,document.documentId,unit.unitId&selected=unit.linkings.taxon.id,media,document.documentId,unit.unitId&includeNonValidTaxa=false&hasUnitMedia=true&cache=true&needsCheck=false&page=1&pageSize=4&access_token=", False)

    # If still no photos, return empty 
    if 0 == data['total']:
        return multimedia, False

    for item in data['results']:
        media = dict()
        if "IMAGE" == item['media']['mediaType']:
            media['licenseAbbreviation'] = item['media']['licenseId']
            media['fullURL'] = item['media']['fullURL']
            media['thumbnailURL'] = item['media']['thumbnailURL']
            media['author'] = item['media']['author']
            media['caption'] = "Havainto/näyte <a href='" + item['document']['documentId'] + "' target='_blank'>" + item['document']['documentId'] + "</a>\n"

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
            elif "taxonDescriptionCaption" in media:
                if "fi" in media['taxonDescriptionCaption']:
                    html += "<span class='caption'>" + media['taxonDescriptionCaption']['fi'] + "</span><br>\n"

            html += "<span class='copyright'>" + media['author'] + ", " + cc_link(media['licenseAbbreviation']) + "</span>"
            html += "</figcaption>\n"

            html += "</figure>\n"
        else:
            html += "<!-- non-cc media -->\n"

    return html


def generate_description(groups):
#    common.print_log(groups[0])
    html = ""
    for group in groups:
#        common.print_log("HERE:")
#        common.print_log(group)
        # Yleistä
        if "MX.SDVG1" == group['group']:
            for variable in group['variables']:
#                html += variable['content']
                if "Ingressi" == variable['title']:
                    html += "<div class='ingressi'>" + variable['content'] + "</div>\n"
                elif "Yleiskuvaus" == variable['title']:
                    html += "<div class='yleiskuvaus'>" + variable['content'] + "</div>\n"
                elif "Tunnistaminen" == variable['title']:
                    html += "<div class='tunnistaminen'>" + variable['content'] + "</div>\n"
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

        if "typeOfOccurrenceInFinland" in species:
            html += "<li>Suomessa "
            for status in species['typeOfOccurrenceInFinland']:
                translated_status = common.map_status(status)
                html += f"{translated_status}, "
        else:
            html += "<li>Ei statustietoa, "

        html += " <a href='/taxa/species/" + qname + "'>lisätietoa &raquo;</a></li>\n"
        
        html += "<li>Laji.fi:ssa <a href='https://laji.fi/observation/map?target=" + qname + "&countryId=ML.206&recordQuality=EXPERT_VERIFIED,COMMUNITY_VERIFIED,NEUTRAL&needsCheck=false'>" + str(species['observationCountFinland']) + " havaintoa Suomesta</a>, <a href='https://laji.fi/taxon/" + qname + "'>lajisivu</a>, <a href='https://laji.fi/taxon/" + qname + "/images'>lisää kuvia</a></li>\n"

        html += "</ul>\n"

        # Photos
        # If no taxon photos, try different sources
        if "multimedia" not in species:
            species['multimedia'], species['hasMultimedia'] = get_additional_multimedia(qname)
#        else:
#            common.print_log(species['multimedia'])


        # Create photo html
        html += "<div class='multimedia'>\n"
        if True == species['hasMultimedia']:
            html += generate_media_html(species['multimedia'], species['qname'])
        else:
            html += "ei vahvistettuja tai museonäytteiden kuvia"
        html += "</div>\n"

        description_html = "<!-- No desc -->\n"
        if "descriptions" in species:
            descriptions = species['descriptions'][0]
            # TODO: Handle if multiple descriptions
            if "groups" in descriptions:
                description_html = generate_description(descriptions['groups'])

        html += f"<div class='desc'>{description_html}\n</div>\n"


#        html += json.dumps(species) # debug
        html += "</div>\n"

    return html


def main(page_name_untrusted):

    html = dict()

    taxon_qname, species_qnames = get_species_qnames(page_name_untrusted)
    
    species_data = get_species_data(species_qnames)

    html["species_html"] = generate_species_html(species_data)

    taxon_data = common.fetch_finbif_api(f"https://api.laji.fi/v0/taxa/{taxon_qname}?lang=fi&langFallback=true&maxLevel=0&includeHidden=false&includeMedia=false&includeDescriptions=false&includeRedListEvaluations=false&sortOrder=taxonomic&access_token=", False)

    html["vernacular_name"] = taxon_data["vernacularName"]
    html["scientific_name"] = taxon_data["scientificName"]

    return html
