import argparse
import datetime
import os
import re


def _today() -> datetime.date:
    return datetime.date.today()


def parse_args(argv: list[str]) -> tuple[datetime.date, datetime.date, list[str], bool]:
    """
    Parse CLI arguments.
    Return (start_date, end_date, providers, skip_confirm).
    """
    parser = argparse.ArgumentParser(description="Timesheet multi-provider")
    parser.add_argument("period", nargs="*", default=[], help="Period: today, week, month, last-month, DD, or DD-MM-YYYY DD-MM-YYYY")
    parser.add_argument("--bamboo", action="store_true", help="BambooHR only")
    parser.add_argument("--productive", action="store_true", help="Productive.io only")
    parser.add_argument("--both", action="store_true", help="Both providers (default)")
    parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")
    args = parser.parse_args(argv)

    today = _today()

    # Providers
    if args.bamboo and not args.productive:
        providers = ["bamboo"]
    elif args.productive and not args.bamboo:
        providers = ["productive"]
    else:
        providers = ["bamboo", "productive"]

    # Period
    period = args.period
    if not period:
        start_date = today
        end_date = today
    elif len(period) == 1:
        token = period[0]
        if token in ("today", "daily"):
            start_date = today
            end_date = today
        elif token in ("week", "weekly"):
            start_date = today - datetime.timedelta(days=today.weekday())
            end_date = today
        elif token in ("month", "monthly"):
            start_date = today.replace(day=1)
            end_date = today
        elif token == "last-month":
            first_of_current = today.replace(day=1)
            end_date = first_of_current - datetime.timedelta(days=1)
            start_date = end_date.replace(day=1)
        else:
            day_num = int(token)
            start_date = today.replace(day=1)
            end_date = today.replace(day=day_num)
    elif len(period) == 2:
        start_date = datetime.datetime.strptime(period[0], "%d-%m-%Y").date()
        end_date = datetime.datetime.strptime(period[1], "%d-%m-%Y").date()
    else:
        parser.error("Too many period arguments")

    return start_date, end_date, providers, args.yes


def working_days(start: datetime.date, end: datetime.date) -> list[datetime.date]:
    """Monday-to-Friday days in the range [start, end]."""
    days = []
    current = start
    while current <= end:
        if current.weekday() < 5:
            days.append(current)
        current += datetime.timedelta(days=1)
    return days


PLACEHOLDER = "xxxx"

FORMATS = {
    "number": (re.compile(r"\d+"), "must be a number"),
    "subdomain": (
        re.compile(r"[a-z0-9-]+"),
        "must be only the subdomain (lowercase letters, digits or '-'), e.g. acme",
    ),
    "secret": (re.compile(r"\S+"), "must not contain spaces"),
}


def config_errors(spec: dict[str, str]) -> list[str]:
    """
    Check environment variables against their expected format.
    Return one message per invalid variable. Values are never echoed,
    since some of them are secrets.
    """
    errors = []
    for name, kind in spec.items():
        value = os.getenv(name, "").strip()
        pattern, problem = FORMATS[kind]
        if not value:
            errors.append(f"{name}: missing")
        elif value == PLACEHOLDER:
            errors.append(f"{name}: still has the example value {PLACEHOLDER}")
        elif not pattern.fullmatch(value):
            errors.append(f"{name}: {problem}")
    return errors
