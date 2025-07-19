"""
Unit tests for the log_analyzer.entry module.

This test suite verifies the behavior of the LogEntry.parse_line() method,
which parses a single log line into a structured LogEntry object.

# Test overview:
- test_parse_valid_line(): Parses a valid log line into all expected fields.
- test_parse_line_with_nepal_timezone(): Parses a valid log line using a custom timezone (Asia/Kathmandu).
- test_log_line_missing_format(): Raises ValueError for lines missing one or more required parts.
- test_wrong_order():  Raises ValueError for lines with incorrect field order.
- test_invalid_timestamp_format(): Raises ValueError for timestamp with incorrect format.
- test_'invalid_range_timestamp(): Raises ValueError when the timestamp is either in the future or to old.
"""

import pytest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from log_analyzer.log_entry import LogEntry, MAX_PAST_YEARS

DEFAULT_LOCAL_TZ = ZoneInfo("Asia/Jerusalem")


def test_parse_valid_line():
    """ Parses a valid log line into all expected fields."""
    line = "2025-07-17T12:00:00 INFO LOGIN User 'bob' logged in"
    entry = LogEntry.parse_line(line)
    expected_ts = datetime.fromisoformat("2025-07-17T12:00:00").replace(tzinfo=ZoneInfo("Asia/Jerusalem"))

    assert entry.timestamp == expected_ts
    assert entry.level == "INFO"
    assert entry.event_type == "LOGIN"
    assert entry.message == "User 'bob' logged in"


def test_parse_line_with_nepal_timezone():
    """Parses a valid log line using a custom timezone (Asia/Kathmandu)."""
    line = "2025-07-17T12:00:00 INFO EVENT Something happened"
    nepal_tz = ZoneInfo("Asia/Kathmandu")
    entry = LogEntry.parse_line(line, local_timezone=nepal_tz)
    expected_ts = datetime.fromisoformat("2025-07-17T12:00:00").replace(tzinfo=nepal_tz)

    assert entry.timestamp == expected_ts
    assert entry.timestamp.tzinfo.key == "Asia/Kathmandu"


def test_log_line_missing_format():
    """ Raises ValueError for lines missing one or more required parts."""
    log = [
        "LEVEL EVENT User 'bob' logged in",                     # missing timestamp
        "2025-07-17T12:00:00 UserLogin EVENT 'bob' logged in",  # missing level
        "2025-07-17T12:00:00  LEVEL 'bob' logged in"            # missing event_type
        "2025-07-17T12:00:00 LEVEL EVENT",                      # missing message
        "2025-07-17T12:00:00 INFO",                             # missing event_type and message,
        "2025-07-17T12:00:00",                                  # missing level, event_type and message
        "",                                                     # empty line
        " ",                                                    # empty line with space
    ]

    for line in log:
        with pytest.raises(ValueError) as exc:
            LogEntry.parse_line(line, local_timezone=DEFAULT_LOCAL_TZ)
        assert "format" in str(exc.value)


def test_wrong_order():
    """  Raises ValueError for lines with incorrect field order. """
    log = [
        "LEVEL EVENT Something happened 2025-07-17T12:00:00"   # wrong order: level,event, msg, timestamp
        "LEVEL 2025-07-17T12:00:00 EVENT Something happened"   # wrong order: level, timestamp, event, msg
        "LEVEL  EVENT 2025-07-17T12:00:00 Something happened"  # wrong order: level, event, timestamp, msg
        "2025-07-17T12:00:00 LEVEL Something happened EVENT"   # wrong order: timestamp, level, msg, event
    ]
    for line in log:
        with pytest.raises(ValueError) as exc:
            LogEntry.parse_line(line)
        assert "format" in str(exc.value)

    valid = "2025-07-17T12:00:00 LEVEL EVENT Something happened"  # correct order: timestamp, level, msg, event
    LogEntry.parse_line(valid)


def test_invalid_timestamp_format():
    """Raises ValueError for timestamp with incorrect format."""
    line = "2025/07/17 12:00:00 LEVEL EVENT invalid timestamp"
    with pytest.raises(ValueError) as exc:
        LogEntry.parse_line(line)


def test_range_timestamp():
    """Raises ValueError if the log line's timestamp is in the future or more than MAX_PAST_YEARS years in the past."""
    future = (datetime.now(DEFAULT_LOCAL_TZ) + timedelta(days=1)).isoformat()
    line = f"{future} LEVEL EVENT Future event"
    with pytest.raises(ValueError) as exc:
        LogEntry.parse_line(line)
    assert "is in the future" in str(exc.value)

    old = (datetime.now(DEFAULT_LOCAL_TZ) - timedelta(days=365 * (MAX_PAST_YEARS + 1))).isoformat()
    line = f"{old} INFO EVENT Ancient event"
    with pytest.raises(ValueError) as exc:
        LogEntry.parse_line(line)
    assert f"more than {MAX_PAST_YEARS} years" in str(exc.value)








