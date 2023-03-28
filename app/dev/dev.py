
from helpers import common_helpers

def get_species_dates(taxon, year):
    
    # TODO: Filter out osb with different start and end dates
    limit = 10000
    url = f"https://api.laji.fi/v0/warehouse/query/unit/list?selected=gathering.conversions.dayOfYearBegin%2Cgathering.conversions.dayOfYearEnd%2Cgathering.conversions.wgs84CenterPoint.lat%2Cgathering.conversions.wgs84CenterPoint.lon&orderBy=gathering.conversions.dayOfYearBegin&pageSize={ limit }&page=1&cache=true&taxonId={ taxon }&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&time={ year }&collectionIdNot=HR.48&individualCountMin=1&qualityIssues=NO_ISSUES&access_token="

    data = common_helpers.fetch_finbif_api(url)
#    print(data)

    observations_count = 0
    observations_string = ""

    for obs in data["results"]:
        # Skip if data is missing
        if "dayOfYearBegin" not in obs["gathering"]["conversions"]:
            continue
        if "wgs84CenterPoint" not in obs["gathering"]["conversions"]:
            continue

        # Skip long date ranges
        if obs["gathering"]["conversions"]["dayOfYearEnd"] > (obs["gathering"]["conversions"]["dayOfYearBegin"] + 10):
            continue

        day = obs["gathering"]["conversions"]["dayOfYearBegin"]
        lat = obs["gathering"]["conversions"]["wgs84CenterPoint"]["lat"]
        lon = obs["gathering"]["conversions"]["wgs84CenterPoint"]["lon"]
        observations_count += 1
        observations_string += f"{{day: {day}, lat: {lat}, lng: {lon}}},"


    return observations_string, observations_count


def main(taxon_qname_untrusted):
    html = dict()

    taxon_qname = common_helpers.valid_qname(taxon_qname_untrusted)
    html['taxon_data'] = common_helpers.taxon_data(taxon_qname)

    # MX.36237 peippo, 17k
    # MX.36239 järri, 4800
    # MX.28895 pöllöt
    # MX.33638 Acrocephalus
    # MX.37992 Betula

    observations_string, observations_count = get_species_dates(taxon_qname, 2022)
    print(observations_count)
#    print(observations_string)

    html["observations_string"] = observations_string

    return html
