import datetime
from unittest.mock import patch, MagicMock
from timesheet.bamboo import is_off_day, has_entries, clock_day


DATE = datetime.date(2026, 4, 10)


def _mock_response(status_code=200, json_data=None):
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data if json_data is not None else []
    mock.text = ""
    return mock


@patch("timesheet.bamboo.requests.get")
def test_is_off_day_true(mock_get):
    mock_get.return_value = _mock_response(200, [
        {"amount": {"amount": 8, "unit": "hours"}}
    ])
    assert is_off_day(DATE) is True


@patch("timesheet.bamboo.requests.get")
def test_is_off_day_false_empty(mock_get):
    mock_get.return_value = _mock_response(200, [])
    assert is_off_day(DATE) is False


@patch("timesheet.bamboo.requests.get")
def test_is_off_day_false_on_error(mock_get):
    mock_get.return_value = _mock_response(500)
    assert is_off_day(DATE) is False


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
