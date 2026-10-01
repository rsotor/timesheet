import datetime
from timesheet.common import working_days


def test_working_days_full_week():
    # Mon Apr 6 to Fri Apr 10
    start = datetime.date(2026, 4, 6)  # Monday
    end = datetime.date(2026, 4, 10)   # Friday
    days = working_days(start, end)
    assert len(days) == 5
    assert all(d.weekday() < 5 for d in days)


def test_working_days_skips_weekend():
    # Thu Apr 9 to Mon Apr 13 (includes Sat 11, Sun 12)
    start = datetime.date(2026, 4, 9)
    end = datetime.date(2026, 4, 13)
    days = working_days(start, end)
    assert len(days) == 3  # Thu, Fri, Mon
    assert datetime.date(2026, 4, 11) not in days
    assert datetime.date(2026, 4, 12) not in days


def test_working_days_single_day_weekday():
    day = datetime.date(2026, 4, 10)  # Friday
    assert working_days(day, day) == [day]


def test_working_days_single_day_weekend():
    day = datetime.date(2026, 4, 11)  # Saturday
    assert working_days(day, day) == []


def test_config_errors_valid(monkeypatch):
    from timesheet.common import config_errors
    monkeypatch.setenv("TS_ID", "13002457")
    monkeypatch.setenv("TS_SUB", "acme-corp")
    monkeypatch.setenv("TS_KEY", "abc123def")
    spec = {"TS_ID": "number", "TS_SUB": "subdomain", "TS_KEY": "secret"}
    assert config_errors(spec) == []


def test_config_errors_missing_and_placeholder(monkeypatch):
    from timesheet.common import config_errors
    monkeypatch.delenv("TS_UNSET", raising=False)
    monkeypatch.setenv("TS_EMPTY", "  ")
    monkeypatch.setenv("TS_EXAMPLE", "xxxx")
    spec = {"TS_UNSET": "secret", "TS_EMPTY": "number", "TS_EXAMPLE": "number"}
    assert config_errors(spec) == [
        "TS_UNSET: missing",
        "TS_EMPTY: missing",
        "TS_EXAMPLE: still has the example value xxxx",
    ]


def test_config_errors_bad_format(monkeypatch):
    from timesheet.common import config_errors
    # Two variables glued on one line (.env without trailing newline)
    monkeypatch.setenv("TS_ID", "13002457BAMBOO_SUBDOMAIN=acme")
    monkeypatch.setenv("TS_SUB", "https://acme.bamboohr.com")
    monkeypatch.setenv("TS_KEY", "abc 123")
    spec = {"TS_ID": "number", "TS_SUB": "subdomain", "TS_KEY": "secret"}
    errors = config_errors(spec)
    assert errors[0] == "TS_ID: must be a number"
    assert errors[1].startswith("TS_SUB: must be only the subdomain")
    assert errors[2] == "TS_KEY: must not contain spaces"
    # Values are never echoed
    assert not any("13002457" in e or "abc" in e for e in errors)
