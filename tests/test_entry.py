"""
Unit tests for the log_analyzer.entry module.

This test suite verifies the behavior of the LogEntry.parse_line() method,
which parses a single log line into a structured LogEntry object.

# Test overview:
- test_parse_valid_line: Parses a valid log line into all expected fields.
- test_parse_line_with_nepal_timezone: Parses a valid log line using a custom timezone (Asia/Kathmandu).
- test_log_line_format: Raises ValueError for malformed lines (e.g. missing fields).
- test_invalid_timestamp_format: Raises ValueError for timestamp with incorrect format.
- test_future_timestamp: Raises ValueError if the log line's timestamp is in the future.
- test_too_old_timestamp: Raises ValueError if the timestamp is older than MAX_PAST_YEARS.
"""


import pytest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from log_analyzer.entry import LogEntry, EXPECTED_LINE_FIELDS, MAX_PAST_YEARS

DEFAULT_LOCAL_TZ = ZoneInfo("Asia/Jerusalem")


def test_parse_valid_line():
    line = "2025-07-17T12:00:00 INFO UserLogin User 'bob' logged in"
    entry = LogEntry.parse_line(line)
    expected_ts = datetime.fromisoformat("2025-07-17T12:00:00").replace(tzinfo=ZoneInfo("Asia/Jerusalem"))

    assert entry.timestamp == expected_ts
    assert entry.level == "INFO"
    assert entry.event_type == "UserLogin"
    assert entry.message == "User 'bob' logged in"


def test_parse_line_with_nepal_timezone():
    line = "2025-07-17T12:00:00 INFO Event Something happened"
    nepal_tz = ZoneInfo("Asia/Kathmandu")
    entry = LogEntry.parse_line(line, local_timezone=nepal_tz)
    expected_ts = datetime.fromisoformat("2025-07-17T12:00:00").replace(tzinfo=nepal_tz)

    assert entry.timestamp == expected_ts
    assert entry.timestamp.tzinfo.key == "Asia/Kathmandu"


@pytest.mark.parametrize(
    "line, description",
    [
        ("INFO UserLogin User 'bob' logged in", "missing timestamp"),
      #  ("2025-07-17T12:00:00 UserLogin User 'bob' logged in", "missing level"),  #TODO - should check it
       # ("2025-07-17T12:00:00 INFO User 'bob' logged in", "missing event_type"),
        ("2025-07-17T12:00:00 INFO UserLogin", "missing message"),
        ("2025-07-17T12:00:00 INFO", "missing event_type and message"),
        ("2025-07-17T12:00:00", "missing level, event_type and message"),
        ("", "empty line"),
    ]
)
def test_log_line_format(line, description):
    with pytest.raises(ValueError) as exc:
        LogEntry.parse_line(line, local_timezone=DEFAULT_LOCAL_TZ)


def test_invalid_timestamp_format():
    line = "2025/07/17 12:00:00 INFO Event Something happened"
    with pytest.raises(ValueError) as exc:
        LogEntry.parse_line(line)
    assert "Invalid timestamp" in str(exc.value)


def test_future_timestamp():
    future = (datetime.now(DEFAULT_LOCAL_TZ) + timedelta(days=1)).isoformat()
    line = f"{future} INFO Event Future event"
    with pytest.raises(ValueError) as exc:
        LogEntry.parse_line(line)
    assert "is in the future" in str(exc.value)


def test_too_old_timestamp():
    old = (datetime.now(DEFAULT_LOCAL_TZ) - timedelta(days=365 * (MAX_PAST_YEARS + 1))).isoformat()
    line = f"{old} INFO Event Ancient event"
    with pytest.raises(ValueError) as exc:
        LogEntry.parse_line(line)
    assert f"more than {MAX_PAST_YEARS} years" in str(exc.value)


