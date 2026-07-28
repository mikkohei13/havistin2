from pymongo import MongoClient

import app_secrets

import sys

def print_log(dict):
    print(dict, sep="\n", file = sys.stdout)


def _client_db():
    client = MongoClient("mongodb+srv://%s:%s@clusterfree0.zps1x.gcp.mongodb.net/?retryWrites=true&w=majority" % (app_secrets.mongodb_user, app_secrets.mongodb_pass))
    return client['havistin']


def connect_db():
    return _client_db()['taxon_photos']


def connect_inat_photo_db():
    return _client_db()['taxon_inat_photo']


def clear_inat_photo_cache():
    """Delete all documents in taxon_inat_photo only. Leaves other collections untouched."""
    return connect_inat_photo_db().delete_many({})


# Note that if you remove some data items, they will persist in mongodb even after upsert
def set_taxon_photos_data(collection, qname, data):
    record_id = collection.update_one({ '_id': qname }, { "$set": data }, True)
    return record_id


def get_taxon_photos_data(collection, qname):
    where = {"_id": qname }
    result_dict = collection.find_one(where)
    return result_dict

