"""
Tests for EventFilter, which determines whether a given LogEntry matches the rules defined in an EventConfig.

This suite verifies filtering behavior based on:
- event_type
- log level
- regex pattern in the log message

Test Overview:
    - test_event_type_only_matches_and_rejects: Validates matching by event_type only, ignoring level and message.
    - test_level_constraint: Validates that matching requires both event_type and level to match.
    - test_pattern_constraint: Validates that matching requires both event_type and level to match.
    - test_combined_constraints: Validates that all three fields (event_type + level + pattern) must match together.
"""


from datetime import datetime
import re
from log_analyzer.event_config import EventConfig
from log_analyzer.event_filter import EventFilter
from log_analyzer.log_entry import LogEntry


def _make_entry(event_type: str, level: str, message: str) -> LogEntry:
    """
    Helper to create a basic LogEntry
    """
    return LogEntry(timestamp=datetime.now(), level=level, event_type=event_type, message=message)


def test_event_type_only_matches_and_rejects():
    """
    Validates matching by event_type only, ignoring level and message.
    """
    configuration_file = EventConfig(event_type="EVENT1", count=False, level=None, pattern=None)
    flt = EventFilter(configuration_file)
    e1 = _make_entry("EVENT1", "LEVEL", "any message")
    e2 = _make_entry("EVENT2", "LEVEL", "any message")

    assert flt.matches(e1) is True
    assert flt.matches(e2) is False


def test_level_constraint():
    """Validates that matching requires both event_type and level to match."""

    configuration_file = EventConfig(event_type="EVENT", count=False, level="LEVEL", pattern=None)
    flt = EventFilter(configuration_file)
    e_ok = _make_entry("EVENT", "LEVEL", "same event, same level")
    e_wrong_level = _make_entry("EVENT", "ERROR", "fail - same event, different level")
    e_wrong_type = _make_entry("OTHER", "LOGIN", "fail - different event, same level")

    assert flt.matches(e_ok) is True
    assert flt.matches(e_wrong_level) is False
    assert flt.matches(e_wrong_type) is False


def test_pattern_constraint():
    """
    Validates that matching requires event_type + regex pattern match in message.
    """
    regex = re.compile(r"Nvidia")
    configuration_file = EventConfig(event_type="EVENT", count=False, level=None, pattern=regex)
    flt = EventFilter(configuration_file)
    e_ok = _make_entry("EVENT", "ERROR", "I would like to work at Nvidia")
    e_no_match = _make_entry("EVENT", "ERROR", "I would like to work somewhere else")
    e_wrong_type = _make_entry("OTHER", "ERROR", "I would like to work at Nvidia")

    assert flt.matches(e_ok) is True
    assert flt.matches(e_no_match) is False
    assert flt.matches(e_wrong_type) is False


def test_combined_constraints():
    """
    Validates that all three fields (event_type + level + pattern) must match together.
    """
    regex = re.compile(r"Nvidia")
    cfg = EventConfig(event_type="TestEvt", count=False, level="WARN", pattern=regex)
    flt = EventFilter(cfg)
    e_good = _make_entry("TestEvt", "WARN", "I would like to work at Nvidia")
    e_bad_message = _make_entry("TestEvt", "WARN", "I would like work somewhere else")
    e_bad_level = _make_entry("TestEvt", "INFO", "I would like to work at Nvidia")
    e_bad_type = _make_entry("Other", "WARN", "I would like to work at Nvidia")

    assert flt.matches(e_good) is True
    assert flt.matches(e_bad_message) is False
    assert flt.matches(e_bad_level) is False
    assert flt.matches(e_bad_type) is False
