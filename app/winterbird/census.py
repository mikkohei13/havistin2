

import re
from helpers import common_helpers
import datetime

import pandas as pd

def format_with_point(x):
    return '{:,.0f}'.format(x).replace(',', '.')


def validate_society_id(id):
    if re.search(r'ML\.\d+', id):
        return id
    common_helpers.print_log("ERROR: Yhdistyksen id ei kelpaa")
    raise ValueError


def validate_season(season):
    # By giving special keyword "nyt" the season is set automatically
    if "nyt" == season:
        now = datetime.datetime.now()
        month_now = now.month
        year_now = now.year
        if 10 == month_now or 11 == month_now:
            return f"{ year_now }-1"
        if 12 == month_now:
            return f"{ year_now }-2"
        if 1 == month_now:
            return f"{ year_now - 1 }-2"
        else:
            return f"{ year_now - 1 }-3"

    # Otherwise validate season given by user
    if re.fullmatch(r'\d{4}-\d', season):
        return season
    common_helpers.print_log("ERROR: Kauden id ei kelpaa")
    raise ValueError


def get_society_info(society_id):
    url = f"https://api.laji.fi/v0/areas/{ society_id }?lang=fi&access_token="
    data_dict = common_helpers.fetch_finbif_api(url)
    return data_dict["name"]


def id_to_qname_link(id):
    qname = id.replace("http://tun.fi/", "")
    return f"<a href='{id}' target='_blank'>{qname}</a>"


def clean_name(name):
    return name
    second_comma_index = name.index(',', name.index(',') + 1)
    return name[:second_comma_index]


def season_to_year_month(season):
    pieces = season.split("-")
    year = int(pieces[0])
    subseason = int(pieces[1])

    print(f"/{subseason}/")

    if 1 == subseason:
        return f"{ year }-10%2F{ year }-11"
    if 2 == subseason:
        return f"{ year }-12%2F{ year + 1 }-01"
    if 3 == subseason:
        return f"{ year + 1 }-02%2F{ year + 1 }-03"
    common_helpers.print_log("ERROR: Laskennan numero ei kelpaa")
    raise ValueError


def datatable(society_id, year_month):
    per_page = 10000

    # Get named place names
    url = f"https://api.laji.fi/v0/named-places?pageSize=1000&collectionID=HR.39&birdAssociationArea={ society_id }&includePublic=true&includeUnits=false&access_token="
    namedplaces_dict = common_helpers.fetch_finbif_api(url)

    places_html = ""
    named_places_lookup = dict()
    for p, place in enumerate(namedplaces_dict["results"]):
        places_html += place["name"] + ", " 
        named_places_lookup[place["id"]] = place["name"]

    # Get all bird observations, aggregated by named place and document
    url = f"https://api.laji.fi/v0/warehouse/query/unit/statistics?aggregateBy=document.documentId%2Cdocument.namedPlace.id%2Cunit.linkings.taxon.nameFinnish%2Cunit.linkings.taxon.taxonomicOrder&orderBy=document.namedPlace.id&onlyCount=true&taxonCounts=false&gatheringCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize={ per_page }&page=1&cache=true&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&birdAssociationAreaId={ society_id }&yearMonth={ year_month }&collectionId=HR.39&individualCountMin=1&qualityIssues=NO_ISSUES&access_token="
    data_dict = common_helpers.fetch_finbif_api(url)

    # order_dict contains all taxa in the data, with taxonomic sort order number
    taxon_order_dict = dict()

    census_observations = dict()
    for i, observation in enumerate(data_dict["results"]):
        document_qname_link = id_to_qname_link(observation["aggregateBy"]["document.documentId"])
        named_place_id = observation["aggregateBy"]["document.namedPlace.id"].replace("http://tun.fi/", "")

        # Skip routes which cannot be found - routes that are on the area of society A, but have been assigned incorrectly for society B
        if named_place_id not in named_places_lookup:
            continue

        named_place_name = clean_name(named_places_lookup[named_place_id])

        # Fill in sort order that contains all the taxa included in the results
        taxon_order_dict[ int(observation["aggregateBy"]["unit.linkings.taxon.taxonomicOrder"]) ] = observation["aggregateBy"]["unit.linkings.taxon.nameFinnish"]

        # Metadata
        heading = f"{named_place_name} {observation['oldestRecord']} {document_qname_link}"
        if heading not in census_observations:
            census_observations[heading] = dict()
        
        # Observations
        census_observations[heading][observation["aggregateBy"]["unit.linkings.taxon.nameFinnish"]] = observation["individualCountSum"]

    # Once the order_dict is filled with all taxa in the data, sort it by taxonomic sort order number. 
    sorted_taxon_order_dict = dict(sorted(taxon_order_dict.items(), key=lambda x: int(x[0])))

    # Make a sorted list with only the taxon names to be sorted
    sorted_taxon_order_list = []
    for k, v in sorted_taxon_order_dict.items():
        sorted_taxon_order_list.append(v)

    # Create dataframe
    df = pd.DataFrame.from_dict(census_observations, orient='columns')

    # Sort the dataframe based on taxon names 
    df = df.sort_index(key=lambda x: [sorted_taxon_order_list.index(i) for i in x])

    # Add sum column
    sum_column = df.sum(axis=1)
    df['Yht.'] = sum_column

    # Add sum row
    sums = pd.DataFrame(df.sum(axis=0)).T
    sums.index = ['Yhteensä']
    df_with_sums = pd.concat([df, sums], axis=0)

    # Do this if you want to transpose species & routes
#    df = df.transpose()

    datatable_html = df_with_sums.to_html(border=0, na_rep="", float_format='{:,.0f}'.format, escape=False, formatters={col: format_with_point for col in df.columns})
    census_count = df_with_sums.shape[1] - 1 # Excludes title column

    return datatable_html, census_count
 

def main(society_id_dirty, season_dirty):
    html = dict()

    if "" == society_id_dirty and "" == season_dirty:
        html["society_name"] = ""
        html["season"] = ""
        html["data"] = ""
        html["count"] = 0
    
    else:
        society_id = validate_society_id(society_id_dirty)
        season = validate_season(season_dirty)
        html["society_name"] = get_society_info(society_id)
        html["season"] = season
        season_year_month = season_to_year_month(season)
        html["data"], html["count"] = datatable(society_id, season_year_month)

    return html
