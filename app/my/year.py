
from helpers import common_helpers
import datetime
import json

import re

def validate_taxon_id(taxon_id):
    pattern = r'^MX\.\d{1,10}$'

    if re.match(pattern, taxon_id):
        return taxon_id
    else:
        return "MX.37600" # default = Biota


def get_day_aggregate(token, year, taxon_id):
    # Todo: Pagination or check if API can give >2000 results
    # Note: timeAccuracy
    url = f"https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=gathering.conversions.dayOfYearBegin&orderBy=gathering.conversions.dayOfYearBegin&onlyCount=true&taxonCounts=false&gatheringCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=367&page=1&cache=true&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&target={ taxon_id }&time={ year }&timeAccuracy=1&individualCountMin=1&wild=WILD,WILD_UNKNOWN&recordQuality=EXPERT_VERIFIED,COMMUNITY_VERIFIED,NEUTRAL&qualityIssues=NO_ISSUES&observerPersonToken={ token }&access_token="

    data_dict = common_helpers.fetch_finbif_api(url)
    return data_dict


def get_species_aggregate(token, year, taxon_id):
    # Todo: Pagination or check if API can give >2000 results
    url = f"https://laji.fi/api/warehouse/query/unit/aggregate?countryId=ML.206&target={ taxon_id }&time={ year }&recordQuality=EXPERT_VERIFIED,COMMUNITY_VERIFIED,NEUTRAL&wild=WILD,WILD_UNKNOWN&individualCountMin=1&aggregateBy=unit.linkings.taxon.speciesId,unit.linkings.taxon.speciesNameFinnish,unit.linkings.taxon.speciesScientificName&selected=unit.linkings.taxon.speciesId,unit.linkings.taxon.speciesNameFinnish,unit.linkings.taxon.speciesScientificName&cache=true&page=1&pageSize=2000&qualityIssues=NO_ISSUES&geoJSON=false&onlyCount=false&observerPersonToken={ token }&access_token="

    data_dict = common_helpers.fetch_finbif_api(url)
    return data_dict


def convert_day_of_year_to_date(day_of_year, year):
    date = datetime.datetime(year, 1, 1) + datetime.timedelta(days=day_of_year - 1)
    return date.strftime("%-d.%-m.")


def create_year_chart_data(data, year):

    # Extracting the 'oldestRecord' from each species and converting them into datetime objects
    oldest_records = [datetime.datetime.strptime(species['oldestRecord'], '%Y-%m-%d') for species in data['results'] if 'oldestRecord' in species]

    # Sorting the dates
    oldest_records.sort()

    # Convert dates to day of year
    day_of_year_records = [date.timetuple().tm_yday for date in oldest_records]

    # Find the maximum day of the year in the records
    max_day = max(day_of_year_records)

    # Counting occurrences of each day of year
    day_counts = {}
    for day in day_of_year_records:
        if day in day_counts:
            day_counts[day] += 1
        else:
            day_counts[day] = 1

    # Creating cumulative count
    cumulative_counts = []
    current_count = 0
    for day in range(1, max_day + 1):
        current_count += day_counts.get(day, 0)
        date_string = convert_day_of_year_to_date(day, year)
        cumulative_counts.append((date_string, current_count))

    # Preparing data for chart
    chart_data = {"days": [day for day, _ in cumulative_counts], "cumulative_counts": [count for _, count in cumulative_counts]}

    return chart_data


def create_day_chart_data(data, year):
    days = []
    counts = []

    # Generate a lookup dictionary of daily observation count
    lookup_data = dict()
    for day in data['results']:
        lookup_data[day['aggregateBy']['gathering.conversions.dayOfYearBegin']] = day['count']

    for day_of_year in range(1, 367):

        date = datetime.datetime(year, 1, 1) + datetime.timedelta(days=day_of_year - 1)
        formatted_date = date.strftime("%d.%m").lstrip("0").replace(".0", ".")
        days.append(formatted_date)

        day_of_year_str = str(day_of_year)
        counts.append(lookup_data.get(day_of_year_str, 0))

    chart_data = dict()
    chart_data["days"] = days
    chart_data["counts"] = counts

    return chart_data

def main(token, year_untrusted, taxon_id_untrusted):

    html = dict()

    taxon_id = validate_taxon_id(taxon_id_untrusted)

    # Validate year
    current_year = datetime.datetime.now().year
    if year_untrusted < 1900:
        year = current_year
    elif year_untrusted > current_year:
        year = current_year
    else:
        year = year_untrusted
    html["year"] = year

    html["species_aggregate"] = get_species_aggregate(token, year, taxon_id)
    html["species_chart_data"] = create_year_chart_data(html["species_aggregate"], year)

    html["day_aggregate"] = get_day_aggregate(token, year, taxon_id)
    html["day_chart_data"] = create_day_chart_data(html["day_aggregate"], year)

    return html
