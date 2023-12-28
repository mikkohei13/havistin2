

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use the application default credentials
cred = credentials.Certificate('/havistin2/app/service-account-key.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

def save_data(collection_name, data):
    """ Saves a dictionary to Firestore in the specified collection. """
    collection_ref = db.collection(collection_name)
    doc_ref = collection_ref.add(data)
    return doc_ref[1].id  # Return the generated document ID

def fetch_data(collection_name, doc_id):
    """ Fetches a document from Firestore by its ID. """
    doc_ref = db.collection(collection_name).document(doc_id)
    doc = doc_ref.get()
    return doc.to_dict() if doc.exists else None
