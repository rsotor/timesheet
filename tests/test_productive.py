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


@patch("timesheet.productive._get_entries", return_value=[])
@patch("timesheet.productive.requests.post")
def test_clock_day_creates_new(mock_post, mock_entries):
    mock_post.return_value = _mock_response(201)
    assert clock_day(DATE) is True


@patch("timesheet.productive._get_entries", return_value=[])
@patch("timesheet.productive.requests.post")
def test_clock_day_create_failure(mock_post, mock_entries):
    mock_post.return_value = _mock_response(422)
    assert clock_day(DATE) is False


@patch("timesheet.productive._get_entries", return_value=[])
@patch("timesheet.productive.requests.post")
def test_clock_day_sends_correct_payload(mock_post, mock_entries):
    mock_post.return_value = _mock_response(201)
    clock_day(DATE)
    body = mock_post.call_args.kwargs.get("json") or mock_post.call_args[1].get("json")
    entry = body["data"]
    assert entry["type"] == "time_entries"
    assert entry["attributes"]["date"] == "2026-04-10"
    assert entry["attributes"]["time"] == 480
    assert entry["relationships"]["person"]["data"]["type"] == "people"
    assert entry["relationships"]["service"]["data"]["type"] == "services"


@patch("timesheet.productive._get_entries", return_value=[
    {"id": "999", "attributes": {"time": 0}}
])
@patch("timesheet.productive.requests.patch")
def test_clock_day_patches_zero_entry(mock_patch, mock_entries):
    """Si hay entrada de 0min, la actualiza con PATCH en vez de crear nueva."""
    mock_patch.return_value = _mock_response(200)
    assert clock_day(DATE) is True
    call_url = mock_patch.call_args[0][0]
    assert "999" in call_url
    body = mock_patch.call_args.kwargs.get("json") or mock_patch.call_args[1].get("json")
    assert body["data"]["attributes"]["time"] == 480
