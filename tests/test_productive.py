import datetime
from unittest.mock import patch, MagicMock
from timesheet.productive import has_entries, clock_day


DATE = datetime.date(2026, 4, 10)


def _mock_response(status_code=200, json_data=None):
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data if json_data is not None else {"data": []}
    mock.text = ""
    return mock


@patch("timesheet.productive.requests.get")
def test_has_entries_true(mock_get):
    mock_get.return_value = _mock_response(200, {"data": [
        {"id": "123", "attributes": {"time": 480}}
    ]})
    assert has_entries(DATE) is True


@patch("timesheet.productive.requests.get")
def test_has_entries_false_empty(mock_get):
    mock_get.return_value = _mock_response(200, {"data": []})
    assert has_entries(DATE) is False


@patch("timesheet.productive.requests.get")
def test_has_entries_false_zero_time(mock_get):
    """Entry exists but with 0 minutes — should not count as existing."""
    mock_get.return_value = _mock_response(200, {"data": [
        {"id": "456", "attributes": {"time": 0}}
    ]})
    assert has_entries(DATE) is False


@patch("timesheet.productive.requests.get")
def test_has_entries_false_on_error(mock_get):
    mock_get.return_value = _mock_response(500)
    assert has_entries(DATE) is False


@patch("timesheet.productive.requests.post")
def test_clock_day_success(mock_post):
    mock_post.return_value = _mock_response(201)
    assert clock_day(DATE) is True


@patch("timesheet.productive.requests.post")
def test_clock_day_failure(mock_post):
    mock_post.return_value = _mock_response(422)
    assert clock_day(DATE) is False


@patch("timesheet.productive.requests.post")
def test_clock_day_sends_correct_payload(mock_post):
    mock_post.return_value = _mock_response(201)
    clock_day(DATE)
    call_kwargs = mock_post.call_args
    body = call_kwargs.kwargs.get("json") or call_kwargs[1].get("json")
    entry = body["data"]
    assert entry["type"] == "time_entries"
    assert entry["attributes"]["date"] == "2026-04-10"
    assert entry["attributes"]["time"] == 480
    assert entry["relationships"]["person"]["data"]["type"] == "people"
    assert entry["relationships"]["service"]["data"]["type"] == "services"
