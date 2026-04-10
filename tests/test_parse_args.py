import datetime
from unittest.mock import patch
from timesheet.common import parse_args


# Freeze "today" to 2026-04-10 (Friday) for deterministic tests
TODAY = datetime.date(2026, 4, 10)


def _parse(args_str: str) -> tuple:
    """Helper: split string into argv and parse with frozen date."""
    argv = args_str.split() if args_str else []
    with patch("timesheet.common._today", return_value=TODAY):
        return parse_args(argv)


def test_no_args_defaults_to_today_both():
    start, end, providers, skip = _parse("")
    assert start == TODAY
    assert end == TODAY
    assert providers == ["bamboo", "productive"]
    assert skip is False


def test_today_keyword():
    start, end, providers, _ = _parse("today")
    assert start == TODAY
    assert end == TODAY


def test_week():
    start, end, _, _ = _parse("week")
    assert start == datetime.date(2026, 4, 6)  # Monday of that week
    assert end == TODAY


def test_month():
    start, end, _, _ = _parse("month")
    assert start == datetime.date(2026, 4, 1)
    assert end == TODAY


def test_last_month():
    start, end, _, _ = _parse("last-month")
    assert start == datetime.date(2026, 3, 1)
    assert end == datetime.date(2026, 3, 31)


def test_numeric_day():
    start, end, _, _ = _parse("22")
    assert start == datetime.date(2026, 4, 1)
    assert end == datetime.date(2026, 4, 22)


def test_explicit_range():
    start, end, _, _ = _parse("15-03-2026 28-03-2026")
    assert start == datetime.date(2026, 3, 15)
    assert end == datetime.date(2026, 3, 28)


def test_bamboo_only():
    _, _, providers, _ = _parse("--bamboo")
    assert providers == ["bamboo"]


def test_productive_only():
    _, _, providers, _ = _parse("--productive")
    assert providers == ["productive"]


def test_both_flag():
    _, _, providers, _ = _parse("--both")
    assert providers == ["bamboo", "productive"]


def test_yes_flag():
    _, _, _, skip = _parse("-y")
    assert skip is True


def test_yes_long_flag():
    _, _, _, skip = _parse("--yes")
    assert skip is True


def test_combined():
    start, end, providers, skip = _parse("month --productive -y")
    assert start == datetime.date(2026, 4, 1)
    assert end == TODAY
    assert providers == ["productive"]
    assert skip is True
