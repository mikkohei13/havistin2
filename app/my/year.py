
from helpers import common_helpers
import datetime

def get_species_aggregate(token, year):

    # Todo: Pagination or check if API can give >2000 results
    url = f"https://laji.fi/api/warehouse/query/unit/aggregate?countryId=ML.206&time={ year }-01-01/{ year }-12-31&recordQuality=EXPERT_VERIFIED,COMMUNITY_VERIFIED,NEUTRAL&wild=WILD,WILD_UNKNOWN&aggregateBy=unit.linkings.taxon.speciesId,unit.linkings.taxon.speciesNameFinnish,unit.linkings.taxon.speciesScientificName&selected=unit.linkings.taxon.speciesId,unit.linkings.taxon.speciesNameFinnish,unit.linkings.taxon.speciesScientificName&cache=false&page=1&pageSize=2000&qualityIssues=NO_ISSUES&geoJSON=false&onlyCount=false&observerPersonToken={ token }&access_token="

#    data_dict = common_helpers.fetch_finbif_api(url)

    print(url)


def main(token, year_untrusted):

    html = dict()

    # Validate year
    current_year = datetime.datetime.now().year
    if year_untrusted < 1900:
        year = current_year
    elif year_untrusted > current_year:
        year = current_year
    else:
        year = year_untrusted

    get_species_aggregate(token, year)



    html["year"] = year

    return html
