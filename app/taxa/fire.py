
'''
from fastapi import FastAPI
from pymongo import MongoClient

#import app_secrets

import json
import sys

def print_log(dict):
    print(dict, sep="\n", file = sys.stdout)


def connect_mongodb():
#    app = FastAPI()

    mongodb_user = "havistin-cache-user"
    mongodb_pass = "x4JAQj6rH4jdwXk"

    #client = pymongo.MongoClient("mongodb+srv://havistin-cache-user:x4JAQj6rH4jdwXk@clusterfree0.zps1x.gcp.mongodb.net/?retryWrites=true&w=majority")
    #db = client.test

    #client = MongoClient('mongodb://%s:%s@mongodb:27017/' % ("root", "example"))

    client = MongoClient("mongodb+srv://%s:%s@clusterfree0.zps1x.gcp.mongodb.net/?retryWrites=true&w=majority" % (mongodb_user, mongodb_pass))

    db = client['havistin']
    taxon_photos_coll = db['taxon_photos']

    return taxon_photos_coll

def get_taxon_photos(collection, taxon_qname):

    where = {"_id": taxon_qname }
    print_log(where)

    resultDict = collection.find_one(where)
    resultJson = json.dumps(resultDict)
    return resultDict

mongodb_collection = connect_mongodb()

print_log(mongodb_collection)

where = {"_id": "MX.1" }
print_log(where)

resultDict = mongodb_collection.find_one(where)
resultJson = json.dumps(resultDict)

#data = get_taxon_photos(mongodb_collection, "MX1")

print_log(resultJson)
'''

'''
app.mongodb_client = MongoClient("mongodb+srv://havistin-cache-user:x4JAQj6rH4jdwXk@clusterfree0.zps1x.gcp.mongodb.net/?retryWrites=true&w=majority")
app.database = app.mongodb_client["havistin"]
print("Connected to Havistin database!")


taxon_photos_coll = app.database['taxon_photos']
result = taxon_photos_coll.find({ '_id': 'MX.1'}).limit(1)

photos_json = json.dumps(result)

print_log(photos_json)

#app.database.{collection}.findOne({query}, {projection})


app.mongodb_client.close()
'''


'''
from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

from models import Book, BookUpdate

router = APIRouter()
@router.get("/", response_description="List all books", response_model=List[Book])
def list_books(request: Request):
    books = list(request.app.database["books"].find(limit=100))
    return books
'''