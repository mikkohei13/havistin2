
import taxa.common as common


def main(taxon_id_untrusted):

    valid_qname = common.valid_qname(taxon_id_untrusted)
    
    html = dict()
    html["taxon_name"] = valid_qname

    data = common.fetch_finbif_api("https://api.laji.fi/v0/taxa/MX.229577/species?onlyFinnish=true&selectedFields=id,vernacularName,scientificName,typeOfOccurrenceInFinland,parent.family.scientificName,observationCountFinland&lang=fi&page=1&pageSize=10&sortOrder=taxonomic&access_token=")

    common.print_log(data)

    return html
