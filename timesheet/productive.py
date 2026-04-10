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

HEADERS = {
    "Content-Type": "application/vnd.api+json",
    "X-Auth-Token": API_TOKEN or "",
    "X-Organization-Id": ORG_ID or "",
}


def has_entries(date: datetime.date) -> bool:
    """True si ya hay entradas de tiempo para ese día."""
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
        return False
    if response.status_code == 200:
        return len(response.json().get("data", [])) > 0
    return False


def clock_day(date: datetime.date) -> bool:
    """Registra 8h (480 min) en Productive. Devuelve True si éxito."""
    date_str = date.strftime("%Y-%m-%d")
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
