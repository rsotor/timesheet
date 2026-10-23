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

# Variable name -> expected format (see common.config_errors)
REQUIRED_ENV = {
    "BAMBOO_SUBDOMAIN": "subdomain",
    "BAMBOO_EMPLOYEE_ID": "number",
    "BAMBOO_API_KEY": "secret",
}


WORKDAY_HOURS = 8


def off_hours(date: datetime.date) -> float:
    """Hours of approved time off on that day (0 to WORKDAY_HOURS).

    A weekday listed with 0 inside an approved request is a public holiday
    the request did not deduct, so it counts as a full day off.
    """
    date_str = date.strftime("%Y-%m-%d")
    url = f"{BASE_URL}/time_off/requests"
    params = {
        "employeeId": EMPLOYEE_ID,
        "start": date_str,
        "end": date_str,
        "status": "approved",
    }
    try:
        response = requests.get(
            url, params=params, auth=(API_KEY, "x"),
            headers={"Accept": "application/json"}, timeout=TIMEOUT,
        )
    except requests.exceptions.RequestException:
        return 0
    if response.status_code != 200:
        return 0

    total = 0.0
    for request in response.json():
        if (request.get("status") or {}).get("status", "approved") != "approved":
            continue
        dates = request.get("dates") or {}
        if date_str not in dates:
            continue
        amount = float(dates[date_str])
        if amount == 0:
            return WORKDAY_HOURS
        unit = (request.get("amount") or {}).get("unit", "days")
        total += amount * WORKDAY_HOURS if unit == "days" else amount
    return min(total, WORKDAY_HOURS)


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


def _segments(hours: float) -> list[tuple[str, str]]:
    """Clock segments from 08:00 with a 13:00-14:00 lunch break."""
    minutes = round(hours * 60)
    segments = []
    for block_start, block_len in ((8 * 60, 5 * 60), (14 * 60, 3 * 60)):
        length = min(minutes, block_len)
        if length <= 0:
            break
        end = block_start + length
        segments.append((f"{block_start // 60:02d}:{block_start % 60:02d}", f"{end // 60:02d}:{end % 60:02d}"))
        minutes -= length
    return segments


def clock_day(date: datetime.date, hours: float = WORKDAY_HOURS) -> bool:
    """Clock the given hours (full day: 08-13, 14-17). Return True on success."""
    date_str = date.strftime("%Y-%m-%d")
    payload = {
        "entries": [
            {"employeeId": EMPLOYEE_ID, "date": date_str, "start": start, "end": end}
            for start, end in _segments(hours)
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
