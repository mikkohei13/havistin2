
#from webbrowser import get
import taxa.common as common
import taxa.common_photos as common_photos


# Here is manually defined which species are "new", this depends on existing literature of that taxon.
def get_species_qnames(page_name_untrusted):
    species = list()

    if "heteroptera_new" == page_name_untrusted:
        taxon_title = "Heteroptera: Corixidae - Miridae"
        description_title = "Suomen luteet -kirjasta puuttuvat lajit"

        '''
        # Test data
        species.append("MX.4994283") # Heterotoma planicornis 

        species.append("MX.5075811") # debug duplicate
        species.append("MX.229664") # debug duplicate
        species.append("MX.230068") # debug duplicate
        species.append("MX.229819") # debug duplicate
        species.append("MX.229815") # debug duplicate
        species.append("MX.4994296") # debug duplicate
        species.append("MX.230542") # debug duplicate
        species.append("MX.230504") # debug duplicate
        '''
        # Real data
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

    elif "heteroptera_new_2" == page_name_untrusted:

        taxon_title = "Heteroptera: Nabidae - Pentatomidae"
        description_title = "Suomen luteet -kirjasta puuttuvat lajit"

        # Nabidae etc.
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

        # Pentatomidae
        species.append("MX.5093768") # Arma custos
        species.append("MX.230504")
        species.append("MX.4994295")
        species.append("MX.4994296")
        species.append("MX.230542")
        species.append("MX.5015646")
        species.append("MX.230548")
        species.append("MX.230556")
        
    elif "heteroptera_near" == page_name_untrusted:

        taxon_title = "Heteroptera"
        description_title = "Suomen lähialueiden lajit"

        species.append("MX.5093770")
        species.append("MX.5093771")
        species.append("MX.5093773")
        species.append("MX.5093774")
        species.append("MX.5093776")
        species.append("MX.5093777")
        species.append("MX.5093786")
        species.append("MX.5093843")
        species.append("MX.5093779")
        species.append("MX.5093781")
        species.append("MX.5093784")
        species.append("MX.5093787")
        species.append("MX.5093788")
        species.append("MX.5093790")
        species.append("MX.5093791")
        species.append("MX.5093794")
        species.append("MX.5093796")
        species.append("MX.5093798")        
        species.append("MX.5093801")        
        species.append("MX.5093803")        
        species.append("MX.5093806")        
        species.append("MX.5093811")        
        species.append("MX.5093812")        
        species.append("MX.5093814")        
        species.append("MX.5093815")        
        species.append("MX.5093816")        
        species.append("MX.5093818") # Mermitelocerus schmidtii


    return taxon_title, description_title, species


def get_species_data(species_qnames):
    species_data = []
    for qname in species_qnames:
        data = common.fetch_finbif_api(f"https://api.laji.fi/v0/taxa/{qname}?lang=fi&langFallback=true&maxLevel=0&includeHidden=true&includeMedia=true&includeDescriptions=true&includeRedListEvaluations=false&sortOrder=taxonomic&access_token=", False)
#        common.print_log(data) # debug
        species_data.append(data)

    return species_data


def generate_description(groups):
    html = ""
    for group in groups:
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

#        common.print_log(species)
        qname = species['qname']
        family = species['parent']['family']['scientificName']

        photos_data = common_photos.get_photos_data(qname, 86400, 6) # 86400 = 24 h

        if family != family_mem:
            html += f"<h2 class='new_family'>{family}</h2>"
            family_mem = family

        html += "\n<div class='species'>\n"
        if "vernacularName" in species:
            vernacular_name = species['vernacularName'].capitalize()
            html += f"<h3>{vernacular_name} - <em>{species['scientificName']}</em> {species['scientificNameAuthorship']}</h3>\n"
        else:
            html += f"<h3><em>{species['scientificName']}</em> {species['scientificNameAuthorship']}</h3>\n"

        html += "<ul class='speciesinfo'>\n"

        '''
        if species['finnishSpecies']:
            html += "<li>SUOMALAINEN</li>"
        else:
            html += "<li>EI-SUOMALAINEN</li>"
        '''

        if "typeOfOccurrenceInFinland" in species:
            html += "<li>Suomessa "
            for status in species['typeOfOccurrenceInFinland']:
                translated_status = common.map_status(status)
                html += f"{translated_status}, "
        else:
            html += "<li>Ei statustietoa, "

        if species["invasiveSpecies"]:
            html += "<span class='invasive'>vieraslaji</span>, "

        html += " <a href='/taxa/species/" + qname + "'>lisätietoa &raquo;</a></li>\n"
        
        html += "<li>Laji.fi:ssa <a href='https://laji.fi/observation/map?target=" + qname + "&countryId=ML.206&recordQuality=EXPERT_VERIFIED,COMMUNITY_VERIFIED,NEUTRAL&needsCheck=false'>" + str(species['observationCountFinland']) + " havaintoa Suomesta</a>, <a href='https://laji.fi/taxon/" + qname + "'>lajisivu</a>, <a href='https://laji.fi/taxon/" + qname + "/images'>lisää kuvia</a></li>\n"

        html += "</ul>\n"

        # Photos
        html += "<div class='multimedia'>\n"

        # For each photo of this taxon
        for photo in photos_data['photos']:
            html += "\n<figure class='photo'>\n"
            html += "<a href='" + str(photo['full_url']) + "'>"
            html += "<img src='" + str(photo['thumbnail_url']) + "'>"
            html += "</a>\n"
            html += "<figcaption>\n"
            html += "<span class='caption'>" + str(photo['caption_plain']) + "</span><br>\n"
            html += "<span class='copyright'>" + str(photo['attribution_plain']) + "</span>\n"
            html += "</figcaption>\n"
            html += "</figure>\n"

        html += "</div>\n"

        description_html = "<!-- No desc -->\n"
        if "descriptions" in species:
            descriptions = species['descriptions'][0]
            # TODO: Handle if multiple descriptions
            if "groups" in descriptions:
                description_html = generate_description(descriptions['groups'])

        html += f"<div class='desc'>{description_html}\n</div>\n"

        html += "</div>\n"

    return html


def main(page_name_untrusted):
    common.print_log("Getting species data...")

    html = dict()
    taxon_title, description_title, species_qnames = get_species_qnames(page_name_untrusted)

    html['taxon_title'] = taxon_title
    html['description_title'] = description_title

#    common.print_log("Getting higher taxon data...")
#    taxon_data = common.fetch_finbif_api(f"https://api.laji.fi/v0/taxa/{taxon_qname}?lang=fi&langFallback=true&maxLevel=0&includeHidden=false&includeMedia=false&includeDescriptions=false&includeRedListEvaluations=false&sortOrder=taxonomic&access_token=", False)

#    common.print_log(taxon_data)
#    return html

    common.print_log("Generating species html...")
    species_data = get_species_data(species_qnames)

    # TODO: Remove subgenus name, if that hinders data fetching from iNat?
    # e.g. Chlamydatus (Chlamydatus) evanescens
    html["species_html"] = generate_species_html(species_data)

    '''
    common.print_log("Finishing up...")
    if "vernacularName" in taxon_data:
        html["vernacular_name"] = taxon_data["vernacularName"]
    else:
        html["vernacular_name"] = "Ei suomenkielistä nimeä"
    html["scientific_name"] = taxon_data["scientificName"]
    '''

    common.print_log("Ready.")
    return html
