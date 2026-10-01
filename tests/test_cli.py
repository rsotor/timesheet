import datetime
from unittest.mock import patch, MagicMock
from timesheet.common import parse_args, working_days


def test_full_flow_no_args_defaults_to_today():
    """No arguments = today + both providers."""
    today = datetime.date(2026, 4, 10)
    with patch("timesheet.common._today", return_value=today):
        start, end, providers, skip = parse_args([])
    assert start == end == today
    assert providers == ["bamboo", "productive"]


def test_full_flow_month_productive_only():
    """month --productive = current month, productive only."""
    today = datetime.date(2026, 4, 10)
    with patch("timesheet.common._today", return_value=today):
        start, end, providers, skip = parse_args(["month", "--productive", "-y"])
    days = working_days(start, end)
    assert start == datetime.date(2026, 4, 1)
    assert end == today
    assert providers == ["productive"]
    assert skip is True
    assert len(days) == 8  # Apr 1-10, 2026 has 8 working days (Apr 4-5 are weekend)
