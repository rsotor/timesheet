import datetime
from unittest.mock import patch, MagicMock
from timesheet.bamboo import off_hours, has_entries, clock_day


DATE = datetime.date(2026, 4, 10)


def _mock_response(status_code=200, json_data=None):
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data if json_data is not None else []
    mock.text = ""
    return mock


def _request(dates, unit="days", status="approved"):
    return {"status": {"status": status}, "amount": {"unit": unit}, "dates": dates}


@patch("timesheet.bamboo.requests.get")
def test_off_hours_full_day(mock_get):
    mock_get.return_value = _mock_response(200, [_request({"2026-04-10": "1"})])
    assert off_hours(DATE) == 8


@patch("timesheet.bamboo.requests.get")
def test_off_hours_half_day(mock_get):
    mock_get.return_value = _mock_response(200, [_request({"2026-04-10": "0.5"})])
    assert off_hours(DATE) == 4


@patch("timesheet.bamboo.requests.get")
def test_off_hours_in_hours_unit(mock_get):
    mock_get.return_value = _mock_response(200, [_request({"2026-04-10": "3"}, unit="hours")])
    assert off_hours(DATE) == 3


@patch("timesheet.bamboo.requests.get")
def test_off_hours_holiday_inside_request_is_full_day(mock_get):
    mock_get.return_value = _mock_response(200, [_request({"2026-04-09": "1", "2026-04-10": "0"})])
    assert off_hours(DATE) == 8


@patch("timesheet.bamboo.requests.get")
def test_off_hours_ignores_not_approved(mock_get):
    mock_get.return_value = _mock_response(200, [_request({"2026-04-10": "1"}, status="superceded")])
    assert off_hours(DATE) == 0


@patch("timesheet.bamboo.requests.get")
def test_off_hours_ignores_other_days(mock_get):
    mock_get.return_value = _mock_response(200, [_request({"2026-04-09": "1"})])
    assert off_hours(DATE) == 0


@patch("timesheet.bamboo.requests.get")
def test_off_hours_capped_at_workday(mock_get):
    mock_get.return_value = _mock_response(200, [
        _request({"2026-04-10": "0.5"}), _request({"2026-04-10": "6"}, unit="hours"),
    ])
    assert off_hours(DATE) == 8


@patch("timesheet.bamboo.requests.get")
def test_off_hours_zero_empty(mock_get):
    mock_get.return_value = _mock_response(200, [])
    assert off_hours(DATE) == 0


@patch("timesheet.bamboo.requests.get")
def test_off_hours_zero_on_error(mock_get):
    mock_get.return_value = _mock_response(500)
    assert off_hours(DATE) == 0


@patch("timesheet.bamboo.requests.get")
def test_has_entries_true(mock_get):
    mock_get.return_value = _mock_response(200, {"1234": {"some": "data"}})
    assert has_entries(DATE) is True


@patch("timesheet.bamboo.requests.get")
def test_has_entries_false_empty(mock_get):
    mock_get.return_value = _mock_response(200, {})
    assert has_entries(DATE) is False


@patch("timesheet.bamboo.requests.post")
def test_clock_day_success(mock_post):
    mock_post.return_value = _mock_response(200)
    assert clock_day(DATE) is True


@patch("timesheet.bamboo.requests.post")
def test_clock_day_failure(mock_post):
    mock_post.return_value = _mock_response(500)
    assert clock_day(DATE) is False


@patch("timesheet.bamboo.requests.post")
def test_clock_day_full_day_segments(mock_post):
    mock_post.return_value = _mock_response(200)
    clock_day(DATE)
    entries = mock_post.call_args.kwargs["json"]["entries"]
    assert [(e["start"], e["end"]) for e in entries] == [("08:00", "13:00"), ("14:00", "17:00")]


@patch("timesheet.bamboo.requests.post")
def test_clock_day_half_day_segments(mock_post):
    mock_post.return_value = _mock_response(200)
    clock_day(DATE, 4)
    entries = mock_post.call_args.kwargs["json"]["entries"]
    assert [(e["start"], e["end"]) for e in entries] == [("08:00", "12:00")]


@patch("timesheet.bamboo.requests.post")
def test_clock_day_six_hours_segments(mock_post):
    mock_post.return_value = _mock_response(200)
    clock_day(DATE, 6.5)
    entries = mock_post.call_args.kwargs["json"]["entries"]
    assert [(e["start"], e["end"]) for e in entries] == [("08:00", "13:00"), ("14:00", "15:30")]
