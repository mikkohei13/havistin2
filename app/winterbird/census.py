

import re
import atlas.common_atlas as common_atlas
from helpers import common_helpers

import pandas as pd


def validate_society_id(id):
    if re.search(r'ML\.\d+', id):
        return id
    common_helpers.print_log("ERROR: Yhdistyksen id ei kelpaa")
    raise ValueError


def validate_season(validate_season):
    if re.fullmatch(r'\d{4}-\d', validate_season):
        return validate_season
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
    '''
    1) Get all bird taxa, aggregated by named place and document
    '''

    per_page = 10000

#    association_id = "ML.1089" # TLY
#    association_id = "ML.1091" # Tringa

    # Named places
    url = f"https://api.laji.fi/v0/named-places?pageSize=1000&collectionID=HR.39&birdAssociationArea={ society_id }&includePublic=true&includeUnits=false&access_token="
    namedplaces_dict = common_helpers.fetch_finbif_api(url)
#    print(namedplaces_dict)

#    return namedplaces_dict, 0

    places_html = ""
    named_places_lookup = dict()
    for p, place in enumerate(namedplaces_dict["results"]):
        places_html += place["name"] + ", " 
        named_places_lookup[place["id"]] = place["name"]


    url = f"https://api.laji.fi/v0/warehouse/query/unit/statistics?aggregateBy=document.documentId%2Cdocument.namedPlace.id%2Cunit.linkings.taxon.nameFinnish%2Cunit.linkings.taxon.taxonomicOrder&orderBy=document.namedPlace.id&onlyCount=true&taxonCounts=false&gatheringCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize={ per_page }&page=1&cache=true&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&birdAssociationAreaId={ society_id }&yearMonth={ year_month }&collectionId=HR.39&individualCountMin=1&qualityIssues=NO_ISSUES&access_token="
    data_dict = common_helpers.fetch_finbif_api(url)
#    print(data_dict)

    # order_dict contains all taxa in the data, with taxonomic sort order number
    taxon_order_dict = dict()

    census_observations = dict()
    for i, observation in enumerate(data_dict["results"]):
        document_qname_link = id_to_qname_link(observation["aggregateBy"]["document.documentId"])
        named_place_id = observation["aggregateBy"]["document.namedPlace.id"].replace("http://tun.fi/", "")
        named_place_name = clean_name(named_places_lookup[named_place_id])

        # Fill in sort order that contains all the taxa included in the results
        taxon_order_dict[ int(observation["aggregateBy"]["unit.linkings.taxon.taxonomicOrder"]) ] = observation["aggregateBy"]["unit.linkings.taxon.nameFinnish"]

        # Metadata
        heading = f"{named_place_name} {observation['oldestRecord']} {document_qname_link}"
        if heading not in census_observations:
            census_observations[heading] = dict()

        # Create & fill in observations data dict
        '''
        if document_id not in census_observations:
            census_observations[document_id] = dict()


        if named_place_name not in census_observations[document_id]:
            census_observations[document_id]["Reitti"] = named_place_name

        if "Päivä" not in census_observations[document_id]:
            census_observations[document_id]["Päivä"] = observation["oldestRecord"]
        '''
        
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
    print(sum_column)
    df['Yht.'] = sum_column

    # Add sum row
    sums = pd.DataFrame(df.sum(axis=0)).T
    sums.index = ['Yhteensä']
    df_with_sums = pd.concat([df, sums], axis=0)

#    df = df.transpose()

#    print(df_with_sums)

    datatable_html = df_with_sums.to_html(border=0, na_rep="", float_format='{:,.0f}'.format, escape=False)
    census_count = df_with_sums.shape[1] - 1 # Excludes title column

    return datatable_html, census_count
 


def main(society_id_dirty, season_dirty):

    society_id = validate_society_id(society_id_dirty)

    season = validate_season(season_dirty)

    html = dict()

    html["society_name"] = get_society_info(society_id)
    html["season"] = season

    season_year_month = season_to_year_month(season)
    print(season_year_month)

    html["data"], html["count"] = datatable(society_id, season_year_month)


    return html
