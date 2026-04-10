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
