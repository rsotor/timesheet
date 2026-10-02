import datetime
from unittest.mock import patch, MagicMock
from timesheet.productive import has_entries, clock_day, needs_submit, submit_day


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
    """If there is a 0-minute entry, PATCH it instead of creating a new one."""
    mock_patch.return_value = _mock_response(200)
    assert clock_day(DATE) is True
    call_url = mock_patch.call_args[0][0]
    assert "999" in call_url
    body = mock_patch.call_args.kwargs.get("json") or mock_patch.call_args[1].get("json")
    assert body["data"]["attributes"]["time"] == 480


def _entry(time=480, submitted=False, approved=False):
    return {"id": "1", "attributes": {"time": time, "submitted": submitted, "approved": approved}}


@patch("timesheet.productive._get_entries", return_value=[_entry()])
def test_needs_submit_logged_not_submitted(mock_entries):
    assert needs_submit(DATE) is True


@patch("timesheet.productive._get_entries", return_value=[_entry(submitted=True)])
def test_needs_submit_already_submitted(mock_entries):
    """Real case: submitted and waiting for approval."""
    assert needs_submit(DATE) is False


@patch("timesheet.productive._get_entries", return_value=[_entry(approved=True)])
def test_needs_submit_approved(mock_entries):
    """Real case: Productive clears `submitted` once the day is approved."""
    assert needs_submit(DATE) is False


@patch("timesheet.productive._get_entries", return_value=[_entry(time=0)])
def test_needs_submit_ignores_zero_minute_entries(mock_entries):
    assert needs_submit(DATE) is False


@patch("timesheet.productive._get_entries", return_value=[])
def test_needs_submit_no_entries(mock_entries):
    assert needs_submit(DATE) is False


@patch("timesheet.productive._get_entries", return_value=[_entry(approved=True), _entry()])
def test_needs_submit_any_pending_entry(mock_entries):
    assert needs_submit(DATE) is True


@patch("timesheet.productive.requests.post")
def test_submit_day_success(mock_post):
    mock_post.return_value = _mock_response(201)
    assert submit_day(DATE) is True


@patch("timesheet.productive.requests.post")
def test_submit_day_rejected_by_api(mock_post):
    mock_post.return_value = _mock_response(422)
    assert submit_day(DATE) is False
