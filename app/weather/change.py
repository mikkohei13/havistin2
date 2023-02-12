
# Tapiola weather

import requests
import json
from datetime import datetime
import time
import sys
from pymongo import MongoClient

import app_secrets


sys.path.append('../')
import messaging.telegram as telegram


def connect_db():
    client = MongoClient("mongodb+srv://%s:%s@clusterfree0.zps1x.gcp.mongodb.net/?retryWrites=true&w=majority" % (app_secrets.mongodb_user, app_secrets.mongodb_pass))
    db = client['havistin']
    collection = db['weatherer']
    return collection


# Note that if you remove some data items, they will persist in mongodb even after upsert
def set_change_event(key):
    unix_time_now = int(time.time())
    document = { "_id": key, "updated": unix_time_now }
    record_id = global_collection.update_one({ "_id": key }, { "$set": document }, upsert = True)
    return record_id


def is_change_event_expired(key):
    where = {"_id": key }
    result_dict = global_collection.find_one(where)
    print(result_dict) # debug

    unix_time_now = int(time.time())
    elapsed_time = unix_time_now - result_dict["updated"]

    if elapsed_time > 3600: # Time to expire in seconds
        return True
    else:
        return False


# Fetch data from API
def fetch_fmi_api(api_url):

    try:
        r = requests.get(api_url)
    except ConnectionError:
        print("ERROR: www.ilmatieteenlaitos.fi/api complete error.")

#    r.encoding = encoding
    dataJson = r.text
    dataDict = json.loads(dataJson)

#    if "status" in dataDict:
#        if 403 == dataDict["status"]:
#            print("ERROR: api.laji.fi 403 error.", file = sys.stdout)
#            raise ConnectionError

#    print(dataDict, file = sys.stdout)
    return dataDict


# Check if time is within given limits
def time_roughly(given, target, margin):
    if given < target - margin:
        return False
    if given > target + margin:
        return False
    return True


# Check if all times exist in the data
def valid_times(observations_dict):
    if 0 not in observations_dict:
        return False
    if 600 not in observations_dict:
        return False
    if 1200 not in observations_dict:
        return False
    if 1800 not in observations_dict:
        return False
    if 2400 not in observations_dict:
        return False
    if 3000 not in observations_dict:
        return False
    if 3600 not in observations_dict:
        return False
    if 4200 not in observations_dict:
        return False
    if 4800 not in observations_dict:
        return False
    if 5400 not in observations_dict:
        return False
    return True


def prettyprint(data):
    print(json.dumps(data, sort_keys = True, indent = 3))


def direction_difference(direction1, direction2):
    # Calculate the absolute difference between the two directions
    diff = abs(direction1 - direction2)
    # If the difference is greater than 180, take the smaller angle
    if diff > 180:
        diff = 360 - diff
    return diff


def trigger_message(data):
    print("Message:")
    print(data)
    print("EOM")

'''
change_value: how much the measurement has been changed. Positive of negative number.
trigger_value: how large change should trigger messaging. Positive number. 
key: key/name of the measurement. String.
secs: in how many seconds has the value changed. Positive integer.
current_value: current value of the measurement. Positive of negative number.
'''
def evaluate_change(change_value, trigger_value, key, secs, current_value):

    # Database key
    if change_value >= 0:
        db_direction = "positive"
    else:
        db_direction = "negative"

    db_key = f"{ key }-{ db_direction }"

    change_value = round(change_value, 1)
    mins = round(secs / 60)


    if abs(change_value) >= trigger_value:
        text = f"{key} change: {change_value} in {mins} minutes, now {current_value}\n"

        if is_change_event_expired(db_key):
            if 1 == global_messaging_on:
                telegram.send_text(text, False)
                set_change_event(db_key)
            else:
                print("Messaging off")
                set_change_event(db_key)
        else:
            print("Previous change not expired")
    else:
        text = f"No {key} change: {change_value} in {mins} minutes, now {current_value}\n"

    return text


def main(messaging_on):

    # TODO: Check when last message about a certain weather event has been sent, don't sent new ones in 1 hour.
    # TODO: Silent messages between 22-23.59 and 00-06.59

    # TODO: Handle these better without passing the collection through multiple functions?
    global global_messaging_on
    global_messaging_on = messaging_on

    global global_collection
    global_collection = connect_db()

    connect_db

    html = ""

    api_url = "https://www.ilmatieteenlaitos.fi/api/weather/observations?fmisid=874863&observations=true&radar=false&daily=false"
    data = fetch_fmi_api(api_url)
    observations = data['observations']

    i = 0
    limit = 10
    latest_unix_time = None

    obs_indexed = {}

    # Create a reversed indexed observation dict
    for obs in reversed(observations):
        dt = datetime.strptime(obs['localtime'], "%Y%m%dT%H%M%S")
        unix_time = dt.timestamp()

        if None == latest_unix_time:
            latest_unix_time = unix_time

        obs_unix_time_diff = latest_unix_time - unix_time
    #    print(obs_unix_time_diff)
    #    print(obs)

        obs_indexed[int(obs_unix_time_diff)] = obs

        i = i + 1
        if i >= limit:
            break

    html += json.dumps(obs_indexed, indent = 3) + "\n"

    if valid_times(obs_indexed) == False:
        html += f"Some times missing:  { obs_indexed }\n"
    else:
        html += "Times ok\n"

    #prettyprint(obs)

    #print(obs_indexed)

    # Check that there are values, they can be missing
    if None == obs_indexed[0]["t2m"]:
        html += "Got None values, exiting..."
        return html


    # Temperature
    key = "t2m"
    # 10 min
    secs = 600
    change = obs_indexed[0][key] - obs_indexed[secs][key]
    html = evaluate_change(change, 2, key, secs, obs_indexed[0][key]) + html

    # 1 hour
    secs = 3600
    change = obs_indexed[0][key] - obs_indexed[secs][key]
    html = evaluate_change(change, 4, key, secs, obs_indexed[0][key]) + html

    # 1,5 hours
    secs = 5400
    change = obs_indexed[0][key] - obs_indexed[secs][key]
    html = evaluate_change(change, 6, key, secs, obs_indexed[0][key]) + html

    # DEBUG temp in production
    secs = 5400
    change = obs_indexed[0][key] - obs_indexed[secs][key]
    html = evaluate_change(change, 2, key, secs, obs_indexed[0][key]) + html

    # Wind
    key = "WindSpeedMS"
    # 10 min
    secs = 600
    change = obs_indexed[0][key] - obs_indexed[secs][key]
    html = evaluate_change(change, 3, key, secs, obs_indexed[0][key]) + html

    # 1 hour
    secs = 3600
    change = obs_indexed[0][key] - obs_indexed[secs][key]
    html = evaluate_change(change, 4, key, secs, obs_indexed[0][key]) + html

    # 1,5 hours
    secs = 5400
    change = obs_indexed[0][key] - obs_indexed[secs][key]
    html = evaluate_change(change, 5, key, secs, obs_indexed[0][key]) + html

    # Cloud cover
    key = "TotalCloudCover"
    # 20 min
    secs = 1200
    change = obs_indexed[0][key] - obs_indexed[secs][key]
    html = evaluate_change(change, 4, key, secs, obs_indexed[0][key]) + html
    # 1.5 h
    secs = 5400
    change = obs_indexed[0][key] - obs_indexed[secs][key]
    html = evaluate_change(change, 6, key, secs, obs_indexed[0][key]) + html

    # Snow depth
    key = "SnowDepth"
    # 1 h
    secs = 3600
    change = obs_indexed[0][key] - obs_indexed[secs][key]
    html = evaluate_change(change, 2, key, secs, obs_indexed[0][key]) + html

    return html

