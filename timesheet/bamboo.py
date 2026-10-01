import datetime
import os
import requests
from dotenv import load_dotenv

load_dotenv()

EMPLOYEE_ID = os.getenv("BAMBOO_EMPLOYEE_ID")
API_KEY = os.getenv("BAMBOO_API_KEY")
SUBDOMAIN = os.getenv("BAMBOO_SUBDOMAIN")
BASE_URL = f"https://{SUBDOMAIN}.bamboohr.com/api/v1"
TIMEOUT = 30

REQUIRED_ENV = ("BAMBOO_SUBDOMAIN", "BAMBOO_EMPLOYEE_ID", "BAMBOO_API_KEY")


def is_off_day(date: datetime.date) -> bool:
    """True if there is an approved time-off request for that day."""
    url = f"{BASE_URL}/time_off/requests"
    params = {
        "employeeId": EMPLOYEE_ID,
        "start": date.strftime("%Y-%m-%d"),
        "end": date.strftime("%Y-%m-%d"),
    }
    try:
        response = requests.get(
            url, params=params, auth=(API_KEY, "x"),
            headers={"Accept": "application/json"}, timeout=TIMEOUT,
        )
    except requests.exceptions.RequestException:
        return False
    if response.status_code == 200:
        entries = response.json()
        if len(entries) > 0:
            return True
    return False


def has_entries(date: datetime.date) -> bool:
    """True if there are already timesheet entries for that day."""
    date_str = date.strftime("%Y-%m-%d")
    url = f"{BASE_URL}/time_tracking/timesheet_entries"
    params = {
        "employeeIds": EMPLOYEE_ID,
        "start": date_str,
        "end": date_str,
    }
    try:
        response = requests.get(
            url, params=params, auth=(API_KEY, "x"), timeout=TIMEOUT,
        )
    except requests.exceptions.RequestException:
        return False
    if response.status_code == 200:
        data = response.json()
        return bool(data)
    return False


def clock_day(date: datetime.date) -> bool:
    """Create two clock entries (08-13, 14-17). Return True on success."""
    date_str = date.strftime("%Y-%m-%d")
    payload = {
        "entries": [
            {
                "employeeId": EMPLOYEE_ID,
                "date": date_str,
                "start": "08:00",
                "end": "13:00",
            },
            {
                "employeeId": EMPLOYEE_ID,
                "date": date_str,
                "start": "14:00",
                "end": "17:00",
            },
        ]
    }
    url = f"{BASE_URL}/time_tracking/clock_entries/store"
    try:
        response = requests.post(
            url, json=payload, auth=(API_KEY, "x"), timeout=TIMEOUT,
        )
    except requests.exceptions.RequestException:
        return False
    return response.status_code in [200, 201]
