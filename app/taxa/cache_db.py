from pymongo import MongoClient

import app_secrets

import sys

def print_log(dict):
    print(dict, sep="\n", file = sys.stdout)


def connect_db():
    client = MongoClient("mongodb+srv://%s:%s@clusterfree0.zps1x.gcp.mongodb.net/?retryWrites=true&w=majority" % (app_secrets.mongodb_user, app_secrets.mongodb_pass))
    db = client['havistin']
    taxon_photos_coll = db['taxon_photos']
    return taxon_photos_coll


# Note that if you remove some data items, they will persist in mongodb even after upsert
def set_taxon_photos_data(collection, qname, data):
    record_id = collection.update_one({ '_id': qname }, { "$set": data }, True)
    return record_id


def get_taxon_photos_data(collection, qname):
    where = {"_id": qname }
    result_dict = collection.find_one(where)
    return result_dict

