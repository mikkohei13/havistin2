
from webbrowser import get
import taxa.common as common

# Here is manually defined which species are "new", this depends on existing literature of that taxon.
def get_list_of_species(qname):
    species = list()
    if "MX.229577" == qname:
        species.append("MX.229815")
        species.append("MX.229819")
        species.append("MX.5075811")

    return species


def main(taxon_id_untrusted):

    valid_qname = common.valid_qname(taxon_id_untrusted)

    species = get_list_of_species(valid_qname)
    
    html = dict()

    taxon_data = common.fetch_finbif_api(f"https://api.laji.fi/v0/taxa/{valid_qname}?lang=fi&langFallback=true&maxLevel=0&includeHidden=false&includeMedia=false&includeDescriptions=false&includeRedListEvaluations=false&sortOrder=taxonomic&access_token=")

    html["vernacular_name"] = taxon_data["vernacularName"]
    html["scientific_name"] = taxon_data["scientificName"]
    html["species"] = species

    return html
