import requests

import json
import sys

import app_secrets

def print_r(dict):
    print("DICT:", file = sys.stdout)
    print(*dict.items(), sep="\n", file = sys.stdout)

def print_debug(data):
    print("DEBUG:", file = sys.stdout)
    print(str(data), file = sys.stdout)

def main(square_id):
    return "Hoi " + square_id + "!!!"
