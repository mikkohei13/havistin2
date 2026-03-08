import time
import random
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import requests

import app_secrets


DIGITRANSIT_URL = "https://api.digitransit.fi/routing/v2/hsl/gtfs/v1"
STOPS = [
    {"display_name": "Kaskisavu->Espoonlahti", "id": "HSL:2431258"},
    {"display_name": "Kaskisavu->Espoon keskus", "id": "HSL:2431255"},
    {"display_name": "Kaurakaski", "id": "HSL:2431238"},
]
NUMBER_OF_DEPARTURES = 5
NUMBER_OF_DEPARTURES_FETCH = 20

# TEMP: Styling helper. Set to False to disable randomized demo states.
ENABLE_DEMO_RANDOMIZATION = False

GRAPHQL_QUERY = """
query StopDepartures($stopId: String!, $numberOfDepartures: Int!) {
  stop(id: $stopId) {
    gtfsId
    name
    code
    stoptimesWithoutPatterns(numberOfDepartures: $numberOfDepartures) {
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


def _format_delay_for_display(delay_seconds):
    if abs(delay_seconds) <= 59:
        return str(delay_seconds)

    sign = "-" if delay_seconds < 0 else ""
    total_seconds = abs(delay_seconds)
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{sign}{minutes}:{seconds:02d}"


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
    payload = {
        "query": GRAPHQL_QUERY,
        "variables": {
            "stopId": "",
            "numberOfDepartures": NUMBER_OF_DEPARTURES_FETCH,
        },
    }
    return headers, payload


def _fetch_single_stop(stop_id):
    headers, payload = _fetch_stop_departures()
    payload["variables"]["stopId"] = stop_id
    response = requests.post(DIGITRANSIT_URL, headers=headers, json=payload, timeout=15)
    response.raise_for_status()
    return response.json()


def _build_demo_departure(base_epoch, line, delay_seconds, status):
    realtime_epoch = base_epoch + delay_seconds
    return {
        "line": line,
        "headsign": "Demo",
        "scheduled_time": _time_hhmm(base_epoch),
        "realtime_time": _time_hhmm(realtime_epoch),
        "delay_seconds": delay_seconds,
        "delay_display": _format_delay_for_display(delay_seconds),
        "status": status,
        "realtime": True,
        "realtime_state": "UPDATED",
        "departure_epoch": base_epoch,
    }


def _apply_demo_randomization(departures):
    # Keep this isolated so removing demo behavior is one-line (toggle constant).
    demo_patterns = [
        {"status": "on_time", "delay_min": -60, "delay_max": 60},
        {"status": "delayed", "delay_min": 120, "delay_max": 480},
        {"status": "early", "delay_min": -480, "delay_max": -120},
    ]
    random.shuffle(demo_patterns)

    # Ensure we have enough rows to show all 3 realtime status styles.
    now_epoch = int(time.time())
    while len(departures) < NUMBER_OF_DEPARTURES:
        idx = len(departures)
        departures.append(_build_demo_departure(
            base_epoch=now_epoch + ((idx + 1) * 300),
            line=f"{500 + idx}",
            delay_seconds=0,
            status="on_time",
        ))

    for i, pattern in enumerate(demo_patterns):
        delay_seconds = random.randint(pattern["delay_min"], pattern["delay_max"])
        departures[i]["realtime"] = True
        departures[i]["status"] = pattern["status"]
        departures[i]["delay_seconds"] = delay_seconds
        departures[i]["delay_display"] = _format_delay_for_display(delay_seconds)
        departures[i]["realtime_time"] = _time_hhmm(departures[i]["departure_epoch"] + delay_seconds)

    return departures


def main():
    html = {
        "stops": [],
        "error": "",
    }

    if app_secrets.digitransit_api_key == "":
        html["error"] = "Digitransit API key missing."
        return html

    for stop_cfg in STOPS:
        stop_data = {
            "display_name": stop_cfg["display_name"],
            "stop_gtfs_id": stop_cfg["id"],
            "stop_code": "",
            "stop_name": "",
            "departures": [],
            "error": "",
        }

        try:
            api_data = _fetch_single_stop(stop_cfg["id"])
        except requests.RequestException:
            stop_data["error"] = "Digitransit request failed."
            html["stops"].append(stop_data)
            continue

        if api_data.get("errors"):
            stop_data["error"] = "Digitransit returned GraphQL errors."
            html["stops"].append(stop_data)
            continue

        stop = api_data.get("data", {}).get("stop")
        if not stop:
            stop_data["error"] = "Stop data not available."
            html["stops"].append(stop_data)
            continue

        stop_data["stop_gtfs_id"] = stop.get("gtfsId") or stop_cfg["id"]
        stop_data["stop_name"] = stop.get("name") or stop_cfg["display_name"]
        stop_data["stop_code"] = stop.get("code") or ""

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
                "delay_display": _format_delay_for_display(departure_delay),
                "status": status,
                "realtime": realtime,
                "realtime_state": stoptime.get("realtimeState", ""),
                "departure_epoch": departure_epoch,
            })

        departures.sort(key=lambda item: item["departure_epoch"])
        if ENABLE_DEMO_RANDOMIZATION:
            departures = _apply_demo_randomization(departures)
        stop_data["departures"] = departures[:NUMBER_OF_DEPARTURES]
        html["stops"].append(stop_data)

    return html
