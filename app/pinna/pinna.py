
from helpers import common_helpers
from helpers import firebase
import datetime
import json

def get_pinna(token):
    return "Hoi maailma!"


def main(token):

    # --------------------
    # Prepare
    html = dict()

    # --------------------
    # Get data

    html["data"] = get_pinna(token)

    return html
