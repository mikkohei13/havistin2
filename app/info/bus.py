import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import requests

import app_secrets


DIGITRANSIT_URL = "https://api.digitransit.fi/routing/v2/hsl/gtfs/v1"
STOP_ID = "HSL:2431258"
STOP_CODE_FALLBACK = "E4320"
STOP_NAME_FALLBACK = "Kaskisavu / Lehtikaskentie"
NUMBER_OF_DEPARTURES = 3 # Change this also to the graphql query

GRAPHQL_QUERY = """
query StopDepartures {
  stop(id: "HSL:2431258") {
    gtfsId
    name
    code
    stoptimesWithoutPatterns(numberOfDepartures: 20) {
      serviceDay
      scheduledDeparture
      realtimeDeparture
      departureDelay
      realtime
      realtimeState
      headsign
      trip {
        gtfsId
        route {
          gtfsId
          shortName
          mode
        }
      }
    }
  }
}
"""


def _status_from_realtime(realtime, departure_delay):
    if not realtime:
        return "scheduled_only"
    if departure_delay > 60:
        return "delayed"
    if departure_delay < -30:
        return "early"
    return "on_time"


def _time_hhmm(epoch_seconds):
    local_dt = datetime.fromtimestamp(epoch_seconds, tz=timezone.utc).astimezone(ZoneInfo("Europe/Helsinki"))
    return local_dt.strftime("%H:%M")


def _get_selected_departure_epoch(stoptime):
    service_day = int(stoptime.get("serviceDay", 0))
    realtime = bool(stoptime.get("realtime", False))
    scheduled_departure = int(stoptime.get("scheduledDeparture", 0))
    realtime_departure = int(stoptime.get("realtimeDeparture", scheduled_departure))

    if realtime:
        return service_day + realtime_departure
    return service_day + scheduled_departure


def _fetch_stop_departures():
    headers = {
        "Content-Type": "application/json",
        "digitransit-subscription-key": app_secrets.digitransit_api_key,
    }
    payload = {"query": GRAPHQL_QUERY}
    response = requests.post(DIGITRANSIT_URL, headers=headers, json=payload, timeout=15)
    response.raise_for_status()
    return response.json()


def main():
    html = {
        "stop_gtfs_id": STOP_ID,
        "stop_code": STOP_CODE_FALLBACK,
        "stop_name": STOP_NAME_FALLBACK,
        "departures": [],
        "error": "",
    }

    if app_secrets.digitransit_api_key == "":
        html["error"] = "Digitransit API key missing."
        return html

    try:
        api_data = _fetch_stop_departures()
    except requests.RequestException:
        html["error"] = "Digitransit request failed."
        return html

    if api_data.get("errors"):
        html["error"] = "Digitransit returned GraphQL errors."
        return html

    stop = api_data.get("data", {}).get("stop")
    if not stop:
        html["error"] = "Stop data not available."
        return html

    html["stop_gtfs_id"] = stop.get("gtfsId") or STOP_ID
    html["stop_name"] = stop.get("name") or STOP_NAME_FALLBACK
    html["stop_code"] = stop.get("code") or STOP_CODE_FALLBACK

    departures = []
    now_epoch = int(time.time())

    for stoptime in stop.get("stoptimesWithoutPatterns", []):
        route = ((stoptime.get("trip") or {}).get("route") or {})
        route_mode = route.get("mode", "")
        route_short_name = str(route.get("shortName", ""))

        if route_mode != "BUS":
            continue

        departure_epoch = _get_selected_departure_epoch(stoptime)
        if departure_epoch < now_epoch:
            continue

        service_day = int(stoptime.get("serviceDay", 0))
        scheduled_departure = int(stoptime.get("scheduledDeparture", 0))
        realtime_departure = int(stoptime.get("realtimeDeparture", scheduled_departure))
        departure_delay = int(stoptime.get("departureDelay", 0))
        realtime = bool(stoptime.get("realtime", False))
        status = _status_from_realtime(realtime, departure_delay)

        scheduled_epoch = service_day + scheduled_departure
        realtime_epoch = service_day + realtime_departure

        departures.append({
            "line": route_short_name,
            "headsign": stoptime.get("headsign", ""),
            "scheduled_time": _time_hhmm(scheduled_epoch),
            "realtime_time": _time_hhmm(realtime_epoch),
            "delay_seconds": departure_delay,
            "status": status,
            "realtime": realtime,
            "realtime_state": stoptime.get("realtimeState", ""),
            "departure_epoch": departure_epoch,
        })

    departures.sort(key=lambda item: item["departure_epoch"])
    html["departures"] = departures[:NUMBER_OF_DEPARTURES]
    return html
