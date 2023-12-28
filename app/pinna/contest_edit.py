
from helpers import common_helpers
from helpers import firebase
import datetime
import json

def get_pinna(token):
    return "Hoi maailma!"


def is_lower_alphanumeric(s):
    return s.isalnum() and s.islower()


def main(token, id_untrusted):

    # --------------------
    # Prepare
    html = dict()

    if is_lower_alphanumeric(id_untrusted):
        contest_id = id_untrusted
    else:
        raise Exception("Invalid contest id") 

    
    # Example Usage
    data_to_save = {'user_id': 'MA.TEST', 'taxon': 'Aves', 'count': 30}
    collection_name = 'pinna_collection'

    # Save the data and get the document ID
    doc_id = firebase.save_data(collection_name, data_to_save)
    print(f"Document saved with ID: {doc_id}")

    # Fetch the data using the document ID
    fetched_data = firebase.fetch_data(collection_name, doc_id)
    print(f"Fetched data: {fetched_data}")


    # --------------------
    # Get data

    html["data"] = get_pinna(token)

    return html
