
from helpers import common_helpers
import datetime
import json
import calendar

import re

def validate_taxon_id(taxon_id):
    pattern = r'^MX\.\d{1,10}$'

    if re.match(pattern, taxon_id):
        return taxon_id
    else:
        return "MX.37600" # default = Biota


def get_day_count(year):
    if calendar.isleap(year):
        return 366
    else:
        return 365


def get_current_day_of_year():
    current_date = datetime.datetime.now()
    day_of_year = current_date.timetuple().tm_yday
    return day_of_year


def get_obs_count(token, year, taxon_id):
    # Note: includes also erroneous & uncertain observations
    url = f"https://api.laji.fi/v0/warehouse/query/unit/count?cache=false&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&individualCountMin=1&qualityIssues=NO_ISSUES&wild=WILD,WILD_UNKNOWN&countryId=ML.206&target={ taxon_id }&time={ year }&observerPersonToken={ token }&access_token="
    data_dict = common_helpers.fetch_finbif_api(url)
    return data_dict["total"]


def get_day_aggregate(token, year, taxon_id):
    # Todo: Pagination or check if API can give >2000 results
    # Note: timeAccuracy
    url = f"https://api.laji.fi/v0/warehouse/query/unit/aggregate?aggregateBy=gathering.conversions.dayOfYearBegin&orderBy=gathering.conversions.dayOfYearBegin&onlyCount=true&taxonCounts=false&gatheringCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=367&page=1&cache=false&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&countryId=ML.206&target={ taxon_id }&time={ year }&timeAccuracy=2&individualCountMin=1&wild=WILD,WILD_UNKNOWN&recordQuality=EXPERT_VERIFIED,COMMUNITY_VERIFIED,NEUTRAL&qualityIssues=NO_ISSUES&observerPersonToken={ token }&access_token="

    data_dict = common_helpers.fetch_finbif_api(url)
    return data_dict


def get_species_aggregate(token, year, taxon_id):
    # Todo: Pagination or check if API can give >2000 results
    url = f"https://api.laji.fi/v0/warehouse/query/unit/aggregate?countryId=ML.206&target={ taxon_id }&time={ year }&recordQuality=EXPERT_VERIFIED,COMMUNITY_VERIFIED,NEUTRAL&wild=WILD,WILD_UNKNOWN&individualCountMin=1&aggregateBy=unit.linkings.taxon.speciesId,unit.linkings.taxon.speciesNameFinnish,unit.linkings.taxon.speciesScientificName&selected=unit.linkings.taxon.speciesId,unit.linkings.taxon.speciesNameFinnish,unit.linkings.taxon.speciesScientificName&cache=false&page=1&pageSize=2000&qualityIssues=NO_ISSUES&geoJSON=false&onlyCount=false&observerPersonToken={ token }&access_token="

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

    # Or generate full year
    max_day = 365

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
    days_with_observations = 0

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
        if day_of_year_str in lookup_data:
            days_with_observations = days_with_observations + 1

    chart_data = dict()
    chart_data["days"] = days
    chart_data["counts"] = counts

    return chart_data, days_with_observations


def get_rarest_species(species_aggregate):
    species_list = []

    with open("data/taxon-data.json") as f:
        taxon_data = json.load(f)

#    print(species_aggregate)
    # Todo: non-finnish species as well, if there are observations from Finland. E.g. MX.52908
    # Todo: higher taxa

    for species in species_aggregate["results"]:
        single_species_dict = dict()
        species_qname = species["aggregateBy"]["unit.linkings.taxon.speciesId"].replace("http://tun.fi/", "")
        if species_qname in taxon_data:

            single_species_dict["id"] = species_qname
            single_species_dict["fi"] = species["aggregateBy"]["unit.linkings.taxon.speciesNameFinnish"]
            single_species_dict["sci"] = species["aggregateBy"]["unit.linkings.taxon.speciesScientificName"]
            single_species_dict["obs"] = taxon_data[species_qname]["obs"]
            single_species_dict["phy"] = taxon_data[species_qname]["phy"]
            single_species_dict["cla"] = taxon_data[species_qname]["cla"]
            single_species_dict["ord"] = taxon_data[species_qname]["ord"]
            single_species_dict["fam"] = taxon_data[species_qname]["fam"]
            single_species_dict["inv"] = taxon_data[species_qname]["inv"]
            single_species_dict["f"] = taxon_data[species_qname]["f"]

            single_species_dict["own_count"] = species["count"]
            single_species_dict["own_oldest"] = species["oldestRecord"]

            species_list.append(single_species_dict)

    sorted_species_list = sorted(species_list, key=lambda x: x['obs'])

    return sorted_species_list[:20] # Top rarest species


def generate_rarest_list(species_list, year):
    html = "<div id='rarest_species'>\n"

    for species in species_list:
        own_obs_link = f"https://laji.fi/observation/map?target={ species['id'] }&countryId=ML.206&time={ year }-01-01%2F{ year }-12-31&recordQuality=COMMUNITY_VERIFIED,NEUTRAL,EXPERT_VERIFIED&wild=WILD_UNKNOWN,WILD&observerPersonToken=true"
        species_link = f"https://laji.fi/taxon/{ species['id'] }"

        html += f"  <div class='rare_species'>\n    <h4>{ species['fi'].capitalize() }<br> <span class='higher_taxa'>{ species['phy'] }: { species['cla'] }: { species['ord'] }: { species['fam'] }:</span> <em>{ species['sci'] }</em></h4>\n    <p><a href='{ species_link }'>{ species['obs'] } havaintoa Suomesta</a>, <a href='{ own_obs_link }'>{ species['own_count'] } omaa havaintoa</a></p>\n  </div>\n"

    html += "</div>\n"
    return html


def generate_year_dropdown(start_year):
    current_year = datetime.datetime.now().year
    html_options = []

    for year in range(current_year, (start_year - 1), -1):
        html_options.append('<option value="{0}">{0}</option>'.format(year))

    return '\n'.join(html_options)


def get_taxon_name(qname):
    url = f"https://api.laji.fi/v0/taxa/{ qname }?lang=fi&langFallback=true&maxLevel=0&includeHidden=false&includeMedia=false&includeDescriptions=false&includeRedListEvaluations=false&onlyFinnish=true&sortOrder=taxonomic&access_token="

    data_dict = common_helpers.fetch_finbif_api(url)

    if "Biota" == data_dict['scientificName']:
        return "kaikki lajit", data_dict['scientificName']
    if "vernacularName" in data_dict:
        return data_dict['vernacularName'], data_dict['scientificName']
    else:
        return "", data_dict['scientificName'] # Finnish name missing


def get_monthly_species_counts(token, year, taxon_id):
    # Note: timeAccuracy
    url = f"https://api.laji.fi/v0/warehouse/query/unit/aggregate?target={ taxon_id }&countryId=ML.206&time={ year }&recordQuality=EXPERT_VERIFIED,COMMUNITY_VERIFIED,NEUTRAL&wild=WILD,WILD_UNKNOWN&timeAccuracy=2&taxonCounts=true&onlyCount=false&cache=false&qualityIssues=NO_ISSUES&aggregateBy=gathering.conversions.month&&selected=gathering.conversions.month&observerPersonToken={ token }&access_token="

    data_dict = common_helpers.fetch_finbif_api(url)
    return data_dict


def generate_monthly_chart(data):

    # Get data from raw data
    monthly_dict = dict()
    for month in data["results"]:
        monthly_dict[int(month["aggregateBy"]["gathering.conversions.month"])] = month["speciesCount"]

    # Generate list of species counts for Chart.js
    species_counts = []
    for month in range(1, 13):
        species_counts.append(monthly_dict.get(month, 0))

    return species_counts


def main(token, year_untrusted, taxon_id_untrusted):

    # --------------------
    # Prepare
    html = dict()

    taxon_id = validate_taxon_id(taxon_id_untrusted)
    html["fi_name"], html["sci_name"] = get_taxon_name(taxon_id)

    # Validate year
    current_year = datetime.datetime.now().year
    if year_untrusted < 1900:
        year = current_year
    elif year_untrusted > current_year:
        year = current_year
    else:
        year = year_untrusted
    html["year"] = year

    # Days in the year so far
    if current_year == year:
        current_date = datetime.datetime.now()
        day_count = current_date.timetuple().tm_yday
    else:
        day_count = get_day_count(year)


    html["year_options"] = generate_year_dropdown(1970)

    # --------------------
    # Get data
    html["species_aggregate"] = get_species_aggregate(token, year, taxon_id)

    # Check if no observations
    if 0 == html["species_aggregate"]["total"]:
        html["got_results"] = False
        return html

    # If observations found, continue
    html["got_results"] = True

    html["species_chart_data"] = create_year_chart_data(html["species_aggregate"], year)

    html["day_aggregate"] = get_day_aggregate(token, year, taxon_id)
    html["day_chart_data"], html["days_with_observations"] = create_day_chart_data(html["day_aggregate"], year)

    html["obs_count"] = get_obs_count(token, year, taxon_id)
    html["obs_count_day"] = round((html["obs_count"] / day_count), 1)

    # Todo: leap years
    html["days_with_observations_percent"] = round(html["days_with_observations"] / day_count * 100, 1)

    rare_species_list = get_rarest_species(html["species_aggregate"])
    html["rarest_species"] = generate_rarest_list(rare_species_list, year)
#    print(rare_species_list)

    html["month_chart_species_data"] = generate_monthly_chart(get_monthly_species_counts(token, year, taxon_id))

    return html
