
import atlas.common_atlas as common_atlas
from helpers import common_helpers


def fetch_completelists_per_square():

    per_page = 10000
    # This sorts the document based on gathering count DESC, i.e. how many units have coordinates.
    url = f"https://api.laji.fi/v0/warehouse/query/gathering/aggregate?aggregateBy=document.documentId%2Cgathering.conversions.ykj10km.lat%2Cgathering.conversions.ykj10km.lon&onlyCount=true&excludeNulls=true&pessimisticDateRangeHandling=false&pageSize={ per_page }&page=1&cache=false&qualityIssues=NO_ISSUES&completeListTaxonId=MX.37580&completeListType=MY.completeListTypeCompleteWithBreedingStatus%2CMY.completeListTypeComplete&access_token=";

    data_dict = common_helpers.fetch_finbif_api(url)

    document_ids = dict()
    squares = dict()

    total_list_count = 0

    for list in data_dict["results"]:
        n = list["aggregateBy"]["gathering.conversions.ykj10km.lat"].split(".")[0]
        e = list["aggregateBy"]["gathering.conversions.ykj10km.lon"].split(".")[0]
        square_id = n + ":" + e

#        print(square_id)

        document_id = list["aggregateBy"]["document.documentId"]

        # Skip duplicates, i.e. documents that span multiple squares
        if document_id in document_ids:
#            print("Skipping duplicate document_id", document_id)
            continue
        else:
            document_ids[document_id] = True

        # Skip documents without coordinates, what are these?
        if len(square_id) != 7:
#            print("Skipping document without coordinates: ", document_id)
            continue

        total_list_count += 1

        if square_id in squares:
            squares[square_id]["list_count"] += 1
            squares[square_id]["text"] += f"<a href=\\'{ document_id }\\' target=\\'_blank\\'>{ document_id }</a> "
        else:
            squares[square_id] = dict()
            squares[square_id]["list_count"] = 1
            squares[square_id]["text"] = f"<a href=\\'{ document_id }\\' target=\\'_blank\\'>{ document_id }</a> "

#    print(squares)

    return squares, total_list_count


def main():
    html = dict()

    square_data, total_list_count = fetch_completelists_per_square()

    total_square_count = 3859
    
    square_count = len(square_data)
    square_proportion = round((square_count / total_square_count * 100), 1)

#    square_data = { "668:338": 0, "669:338": 10, "670:338": 20, "671:338": 30, "672:338": 40, "673:338": 50, "674:338": 60, "675:338": 70, "676:338": 80, "677:338": 90, "678:338": 100  }

    html["stats"] = f"{ total_list_count } täydellistä listaa { square_count } ruudusta, eli { square_proportion } % kaikista ruuduista."

    html["coordinates"] = common_helpers.squares_with_data(square_data, common_helpers.color_viridis_capped, common_helpers.text_completelists)

    return html
