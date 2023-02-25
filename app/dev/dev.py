
#import json
#import random
import re
import atlas.common_atlas as common_atlas
from helpers import common_helpers

import pandas as pd
#import matplotlib.cm as cm
#import numpy as np


def id_to_qname_link(id):
    qname = id.replace("http://tun.fi/", "")
    return f"<a href='{id}' target='_blank'>{qname}</a>"


def clean_name(name):
    second_comma_index = name.index(',', name.index(',') + 1)
    return name[:second_comma_index]


def datatable():
    '''
    1) Get all bird taxa, aggregated by named place and document
    '''

    # Documents
    year_month = "2022-12%2F2023-01"
    year_month = "2023-02%2F2023-03"

    per_page = 10000

    association_id = "ML.1089" # TLY
    association_id = "ML.1091" # Tringa

    # Named places
    url = f"https://api.laji.fi/v0/named-places?pageSize=1000&collectionID=HR.39&birdAssociationArea={ association_id }&includePublic=true&includeUnits=false&access_token="
    namedplaces_dict = common_helpers.fetch_finbif_api(url)
#    print(namedplaces_dict)

#    return namedplaces_dict, 0

    places_html = ""
    named_places_lookup = dict()
    for p, place in enumerate(namedplaces_dict["results"]):
        places_html += place["name"] + ", " 
        named_places_lookup[place["id"]] = place["name"]


    url = f"https://api.laji.fi/v0/warehouse/query/unit/statistics?aggregateBy=document.documentId%2Cdocument.namedPlace.id%2Cunit.linkings.taxon.nameFinnish%2Cunit.linkings.taxon.taxonomicOrder&orderBy=document.namedPlace.id&onlyCount=true&taxonCounts=false&gatheringCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize={ per_page }&page=1&cache=true&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&birdAssociationAreaId={ association_id }&yearMonth={ year_month }&collectionId=HR.39&individualCountMin=1&qualityIssues=NO_ISSUES&access_token="
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

    print(taxon_order_dict)

    # Once the order_dict is filled with all taxa in the data, sort it by taxonomic sort order number. 
    sorted_taxon_order_dict = dict(sorted(taxon_order_dict.items(), key=lambda x: int(x[0])))

    print(sorted_taxon_order_dict)

    # Make a sorted list with only the taxon names to be sorted
    sorted_taxon_order_list = []
    for k, v in sorted_taxon_order_dict.items():
        sorted_taxon_order_list.append(v)

    print(sorted_taxon_order_list)

    # Create dataframe
    df = pd.DataFrame.from_dict(census_observations, orient='columns')

    # Sort the dataframe based on taxon names 
    df = df.sort_index(key=lambda x: [sorted_taxon_order_list.index(i) for i in x])

#    df = df.transpose()

#    print(df)

    datatable_html = df.to_html(border=0, na_rep="", float_format='{:,.0f}'.format, escape=False)
    census_count = df.shape[1] - 1 # Excludes title column

    return datatable_html, census_count
 


def main(some):
    html = dict()

    html["data"], html["count"] = datatable()


    return html
