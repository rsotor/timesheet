import datetime
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("PRODUCTIVE_API_TOKEN")
ORG_ID = os.getenv("PRODUCTIVE_ORG_ID")
PERSON_ID = os.getenv("PRODUCTIVE_PERSON_ID")
SERVICE_ID = os.getenv("PRODUCTIVE_SERVICE_ID")
BASE_URL = "https://api.productive.io/api/v2"
TIMEOUT = 30

# Variable name -> expected format (see common.config_errors)
REQUIRED_ENV = {
    "PRODUCTIVE_API_TOKEN": "secret",
    "PRODUCTIVE_ORG_ID": "number",
    "PRODUCTIVE_PERSON_ID": "number",
    "PRODUCTIVE_SERVICE_ID": "number",
}

HEADERS = {
    "Content-Type": "application/vnd.api+json",
    "X-Auth-Token": API_TOKEN or "",
    "X-Organization-Id": ORG_ID or "",
}


def _get_entries(date: datetime.date) -> list:
    """Return the time entries for that day."""
    date_str = date.strftime("%Y-%m-%d")
    url = f"{BASE_URL}/time_entries"
    params = {
        "filter[person_id]": PERSON_ID,
        "filter[after]": date_str,
        "filter[before]": date_str,
    }
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
    except requests.exceptions.RequestException:
        return []
    if response.status_code == 200:
        return response.json().get("data", [])
    return []


def has_entries(date: datetime.date) -> bool:
    """True if there are entries with actual time (>0 min) for that day."""
    return any(e.get("attributes", {}).get("time", 0) > 0 for e in _get_entries(date))


def clock_day(date: datetime.date) -> bool:
    """Log 8h (480 min) in Productive. Update an existing 0-minute entry if present."""
    date_str = date.strftime("%Y-%m-%d")

    # If there is a 0-minute entry, update it instead of creating a duplicate
    for entry in _get_entries(date):
        if entry.get("attributes", {}).get("time", 0) == 0:
            entry_id = entry["id"]
            payload = {
                "data": {
                    "type": "time_entries",
                    "id": entry_id,
                    "attributes": {"time": 480},
                }
            }
            url = f"{BASE_URL}/time_entries/{entry_id}"
            try:
                response = requests.patch(url, json=payload, headers=HEADERS, timeout=TIMEOUT)
            except requests.exceptions.RequestException:
                return False
            return response.status_code == 200

    # No previous entry, create a new one
    payload = {
        "data": {
            "type": "time_entries",
            "attributes": {
                "date": date_str,
                "time": 480,
            },
            "relationships": {
                "person": {
                    "data": {"type": "people", "id": PERSON_ID}
                },
                "service": {
                    "data": {"type": "services", "id": SERVICE_ID}
                },
            },
        }
    }
    url = f"{BASE_URL}/time_entries"
    try:
        response = requests.post(url, json=payload, headers=HEADERS, timeout=TIMEOUT)
    except requests.exceptions.RequestException:
        return False
    return response.status_code == 201


def submit_day(date: datetime.date) -> str:
    """Submit the given day for approval. Return 'done', 'exists' or 'error'."""
    date_str = date.strftime("%Y-%m-%d")
    payload = {
        "data": {
            "type": "timesheets",
            "attributes": {"date": date_str},
            "relationships": {
                "person": {"data": {"type": "people", "id": PERSON_ID}},
            },
        }
    }
    url = f"{BASE_URL}/timesheets"
    try:
        response = requests.post(url, json=payload, headers=HEADERS, timeout=TIMEOUT)
    except requests.exceptions.RequestException:
        return "error"
    if response.status_code == 201:
        return "done"
    if response.status_code == 422:
        return "exists"
    return "error"
