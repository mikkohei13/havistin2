
from fastapi import FastAPI
from pymongo import MongoClient

app = FastAPI()

#client = pymongo.MongoClient("mongodb+srv://havistin-cache-user:x4JAQj6rH4jdwXk@clusterfree0.zps1x.gcp.mongodb.net/?retryWrites=true&w=majority")
#db = client.test

#@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient("mongodb+srv://havistin-cache-user:x4JAQj6rH4jdwXk@clusterfree0.zps1x.gcp.mongodb.net/?retryWrites=true&w=majority")
    app.database = app.mongodb_client["pymongo_tutorial"]
    print("Connected to the MongoDB database!")

#@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()

startup_db_client()
shutdown_db_client()

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