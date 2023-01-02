from pymongo import MongoClient

import app_secrets
import taxa.common as common

import sys
import time

def print_log(dict):
    print(dict, sep="\n", file = sys.stdout)


def connect_db():
    client = MongoClient("mongodb+srv://%s:%s@%s/?retryWrites=true&w=majority" % (app_secrets.mongodb_user, app_secrets.mongodb_pass, app_secrets.mongodb_server))
    db = client['havistin']
    coll = db['cache']
    return coll


# Note that if you remove some data items, they will persist in mongodb even after upsert
def set_data(collection, id, data):
    time_cached = int(time.time())
    record_id = collection.update_one({ '_id': id }, { "$set": { "data": data, "time_cached": time_cached } }, True)
    return record_id


def get_data(collection, id):
    where = {"_id": id }
    result_dict = collection.find_one(where)
    if result_dict:
        return result_dict
    else:
        return False


# Todo: if fails to find, what returns?
def get_cached(url, max_time):
#    max_time = 60
    db_coll = connect_db()
    result_dict = get_data(db_coll, url)
    time_now = int(time.time())
    if not result_dict:
        common.print_log("No data in cache for " + url)
        return False
    else:
        age = time_now - result_dict['time_cached']
        if age > max_time:
            common.print_log("Cache data too old (" + str(age) + " secs) for " + url)
            return False
        else:        
            common.print_log("Found fresh data (" + str(age) + " secs) from cache for " + url)
            return result_dict['data']


def set_cached(url, html):
#    common.print_log(html)
    db_coll = connect_db()
    set_data(db_coll, url, html)
    common.print_log("Set cache for " + url)
    return id

'''
def get_cached_deco(func):
    def wrapper():

        func()
    return wrapper
'''

