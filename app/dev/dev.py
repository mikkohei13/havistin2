
#import json
#import random
import atlas.common_atlas as common_atlas
from helpers import common_helpers

import pandas as pd
#import matplotlib.cm as cm
#import numpy as np

def datatable():
    '''
    V2
    1) get named places and documents
    2) get bird taxa for each named place, aggregated by document (so that documents can be handled separately)
    '''

    # Documents and named places
    year_month = "2022-12%2F2023-01"
    per_page = 10

    association_id = "ML.1091" # Tringa

    # This sorts the document based on gathering count DESC, i.e. how many units have coordinates.
    url = f"https://api.laji.fi/v0/warehouse/query/gathering/statistics?aggregateBy=document.documentId%2Cdocument.namedPlaceId&orderBy=%2Cdocument.documentId%2Cdocument.namedPlaceId&onlyCount=true&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize={ per_page }&page=1&cache=true&birdAssociationAreaId={ association_id }&yearMonth={ year_month }&collectionId=HR.39&qualityIssues=NO_ISSUES&access_token=";

    data_dict = common_helpers.fetch_finbif_api(url)
    print(data_dict)

    for i, document in enumerate(data_dict["results"]):
        print(i, document["aggregateBy"]["document.namedPlaceId"])

        named_place_id = document["aggregateBy"]["document.namedPlaceId"]

        # v1
        url = f"https://api.laji.fi/v0/warehouse/query/unit/statistics?aggregateBy=unit.linkings.taxon.speciesNameFinnish%2Cunit.linkings.taxon.speciesTaxonomicOrder&orderBy=%2Cunit.linkings.taxon.speciesTaxonomicOrder&onlyCount=true&taxonCounts=false&gatheringCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=100&page=1&cache=true&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&namedPlaceId={ named_place_id }&yearMonth=2022-12%2F2023-01&collectionId=HR.39&individualCountMin=1&qualityIssues=NO_ISSUES&access_token="

        # v2
        url = f"https://api.laji.fi/v0/warehouse/query/unit/statistics?aggregateBy=document.documentId%2Cdocument.namedPlace.id%2Cunit.linkings.taxon.nameFinnish%2Cunit.linkings.taxon.orderId&orderBy=document.namedPlace.id%2Cunit.linkings.taxon.orderId&onlyCount=true&taxonCounts=false&gatheringCounts=false&pairCounts=false&atlasCounts=false&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize=100&page=1&cache=false&taxonId=MX.37580&useIdentificationAnnotations=true&includeSubTaxa=true&includeNonValidTaxa=true&namedPlaceId={ named_place_id }&yearMonth=2022-12%2F2023-01&collectionId=HR.39&individualCountMin=1&qualityIssues=NO_ISSUES&access_token="

        data_dict = common_helpers.fetch_finbif_api(url)
        print(data_dict)


    # https://api.laji.fi/warehouse/query/unit/statistics?taxonId=
    # &collectionId=HR.39&namedPlaceId=MNP.25278
    # 
    # &aggregateBy=unit.linkings.taxon.speciesId,unit.linkings.taxon.speciesNameFinnish,gathering.conversions.year,gathering.conversions.month,unit.linkings.taxon.speciesTaxonomicOrder&selected=unit.linkings.taxon.speciesId,unit.linkings.taxon.speciesNameFinnish,gathering.conversions.year,gathering.conversions.month,unit.linkings.taxon.speciesTaxonomicOrder&orderBy=unit.linkings.taxon.speciesTaxonomicOrder&page=1&pageSize=10000&onlyCount=false&access_token=bOzxQvW7EppFyAww5nskaGFxGgIdh4olBF1RmQvd8tAZPbMYsA9bUTaWYu2WFeZR


desired_order = [
    'Reitti',
    'Päivä',
    'Erä',
    'käpytikka',
    'harakka',
    'hippiäinen',
    'mustarastas',
    'naakka',
    'närhi',
    'punatulkku',
    'sinitiainen',
    'talitiainen',
    'töyhtötiainen'
    ]

def datatable2():
    '''
    1) Get all bird taxa, aggregated by named place and document
    '''

    # Documents
    year_month = "2022-12%2F2023-01"
    per_page = 100

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

    order_dict = dict()

    census_observations = dict()
    for i, observation in enumerate(data_dict["results"]):
        document_id = observation["aggregateBy"]["document.documentId"]
        named_place_id = observation["aggregateBy"]["document.namedPlace.id"].replace("http://tun.fi/", "")
        named_place_name = named_places_lookup[named_place_id]

        # Fill in sort order that contains all the taxa included in the results
        order_dict[ int(observation["aggregateBy"]["unit.linkings.taxon.taxonomicOrder"]) ] = observation["aggregateBy"]["unit.linkings.taxon.nameFinnish"]

        # Create & fill in observations data dict
        if document_id not in census_observations:
            census_observations[document_id] = dict()

        # Metadata
        if document_id not in census_observations[document_id]:
            census_observations[document_id]["Erä"] = document_id

        if named_place_name not in census_observations[document_id]:
            census_observations[document_id]["Reitti"] = named_place_name

        if "Päivä" not in census_observations[document_id]:
            census_observations[document_id]["Päivä"] = observation["oldestRecord"]
        
        # Observations
        census_observations[document_id][observation["aggregateBy"]["unit.linkings.taxon.nameFinnish"]] = observation["individualCountSum"]

#    print(place_taxa)

    order_dict[1] = "Reitti"
    order_dict[2] = "Päivä"
    order_dict[3] = "Erä"

#    print(order_dict)

    sorted_order_dict = dict(sorted(order_dict.items(), key=lambda x: int(x[0])))

    print(sorted_order_dict)

    newsort = []
    for k, v in sorted_order_dict.items():
        newsort.append(v)

    print(newsort)

    # Create table
    df = pd.DataFrame.from_dict(census_observations, orient='columns')

    # Sort
    df = df.sort_index(key=lambda x: [newsort.index(i) for i in x])
#    df = df.sort_values(by='index', key=lambda x: x.map(sorted_order_dict)) # error
#    df = df.sort_index(key=lambda x: x.map(sorted_order_dict)) # does not work

    print(df)


    return "foo", p
 


def main(some):
    html = dict()

    html["data"], html["count"] = datatable2()


    return html
