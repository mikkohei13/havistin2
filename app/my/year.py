
from helpers import common_helpers
import datetime
import json


def get_species_aggregate(token, year, taxon_id = "MX.37600"):
    # Todo: Pagination or check if API can give >2000 results
    url = f"https://laji.fi/api/warehouse/query/unit/aggregate?countryId=ML.206&target={ taxon_id }&time={ year }-01-01/{ year }-12-31&recordQuality=EXPERT_VERIFIED,COMMUNITY_VERIFIED,NEUTRAL&wild=WILD,WILD_UNKNOWN&aggregateBy=unit.linkings.taxon.speciesId,unit.linkings.taxon.speciesNameFinnish,unit.linkings.taxon.speciesScientificName&selected=unit.linkings.taxon.speciesId,unit.linkings.taxon.speciesNameFinnish,unit.linkings.taxon.speciesScientificName&cache=false&page=1&pageSize=2000&qualityIssues=NO_ISSUES&geoJSON=false&onlyCount=false&observerPersonToken={ token }&access_token="

    data_dict = common_helpers.fetch_finbif_api(url)
    return data_dict


def convert_day_of_year_to_date(day_of_year, year):
    date = datetime.datetime(year, 1, 1) + datetime.timedelta(days=day_of_year - 1)
    return date.strftime("%-d.%-m.")


def create_chart_data(data, year):

    # Extracting the 'oldestRecord' from each species and converting them into datetime objects
    oldest_records = [datetime.datetime.strptime(species['oldestRecord'], '%Y-%m-%d') for species in data['results'] if 'oldestRecord' in species]

    # Sorting the dates
    oldest_records.sort()

    # Convert dates to day of year
    day_of_year_records = [date.timetuple().tm_yday for date in oldest_records]

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
    for day in range(1, 367):
        current_count += day_counts.get(day, 0)
        date_string = convert_day_of_year_to_date(day, year)
        cumulative_counts.append((date_string, current_count))

    # Preparing data for chart
    chart_data = {"days": [day for day, _ in cumulative_counts], "cumulative_counts": [count for _, count in cumulative_counts]}

    return chart_data




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
    html["year"] = year

    html["data"] = get_species_aggregate(token, year, "MX.53078") # MX.37580 birds
    html["chart_data"] = create_chart_data(html["data"], year)

    return html
