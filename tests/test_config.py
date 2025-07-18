"""
Unit tests for the log_analyzer.entry module:

This test suite verifies the behavior of the `load_configs` function,
including parsing of event rules from configuration files, handling of
comments, blank lines, and supported flags: [--count, --level, --pattern]

Test overview:
- test_load_single_event: Load a config with a single event (no flags).
- test_count_flag: Parse and apply the --count flag.
- test_level_flag: Parse and apply the --level flag.
- test_missing_level_value_raises_error: Missing value after --level.
- test_pattern_flag: Parse and apply the --pattern flag.
- test_missing_pattern_value_raises_error: Missing value after --pattern.
- test_invalid_flag_raises_error: Unknown flag should raise an error.
- test_all_flags_combined: Use all supported flags in one rule.
- est_invalid_pattern_regex_raises: Verifies that the flags can be mixed arbitrarily
- test_skip_comments_and_blank_lines: Skip comments and empty lines.
- test_empty_or_comments_only: Empty file or comment-only file → empty config.
"""

import re
import pytest
from log_analyzer.config import load_configs, EventConfig

CFG_NAME = "events.txt"
LEVEL_FLAG = "--level"
COUNT_FLAG = "--count"
PATTERN_FLAG = "--pattern"


def test_load_single_event(tmp_path):
    # Creat a temporary configuration's file and load it
    configuration_file = tmp_path / CFG_NAME
    configuration_file.write_text("LoginEvent")
    configs = load_configs(str(configuration_file))

    assert len(configs) == 1
    c = configs[0]
    assert isinstance(c, EventConfig)
    assert c.event_type == "LoginEvent"
    assert c.count is False
    assert c.level is None
    assert c.pattern is None


def test_count_flag(tmp_path):
    # Creat a temporary valid configuration's file with --count and load it
    configuration_file = tmp_path / CFG_NAME
    configuration_file.write_text(f"LoginEvent {COUNT_FLAG}")

    # Act
    configs = load_configs(str(configuration_file))

    # Assert
    assert len(configs) == 1
    c = configs[0]
    assert isinstance(c, EventConfig)
    assert c.event_type == "LoginEvent"
    assert c.count is True      # <-- should be True now
    assert c.level is None
    assert c.pattern is None


def test_level_flag(tmp_path):
    cfg_file = tmp_path / CFG_NAME
    cfg_file.write_text(f"DataExport {LEVEL_FLAG} WARNING")
    # Act
    configs = load_configs(str(cfg_file))
    # Assert
    assert len(configs) == 1
    c = configs[0]
    assert c.event_type == "DataExport"
    assert c.count is False
    assert c.level == "WARNING"
    assert c.pattern is None


def test_missing_level_value_raises_error(tmp_path):
    path = tmp_path / CFG_NAME
    path.write_text("EventX --level")
    with pytest.raises(ValueError, match="Missing value"):
        load_configs(str(path))


def test_pattern_flag(tmp_path):
    # Pattern should compile a regex
    regex = r"\d+\s+items"
    cfg_file = tmp_path / CFG_NAME
    # quote the pattern so shlex.split sees it as one token
    cfg_file.write_text(f"UploadEvent {PATTERN_FLAG} \"{regex}\"")
    # Act
    configs = load_configs(str(cfg_file))
    assert len(configs) == 1
    c = configs[0]
    assert c.event_type == "UploadEvent"
    assert c.count is False
    assert c.level is None
    assert isinstance(c.pattern, re.Pattern)
    assert c.pattern.pattern == regex


def test_missing_pattern_value_raises_error(tmp_path):
    cfg = tmp_path / CFG_NAME
    cfg.write_text("SomethingHappened --pattern")
    with pytest.raises(ValueError, match="Missing value"):
        load_configs(str(cfg))


def test_invalid_pattern_regex_raises(tmp_path):
    cfg = tmp_path / "events.txt"
    cfg.write_text(f"BadPattern {PATTERN_FLAG} \"[unclosed\"")
    with pytest.raises(re.error):
        load_configs(str(cfg))


def test_invalid_flag_raises_error(tmp_path):
    path = tmp_path / CFG_NAME
    path.write_text("EventX --invalid")
    with pytest.raises(ValueError, match="Invalid flag"):
        load_configs(str(path))


def test_all_flags_combined(tmp_path):
    path = tmp_path / CFG_NAME
    path.write_text(f"Login {COUNT_FLAG} {LEVEL_FLAG} ERROR {PATTERN_FLAG} 'failed'")
    configs = load_configs(str(path))
    config = configs[0]
    assert config.event_type == "Login"
    assert config.count is True
    assert config.level == "ERROR"
    assert config.pattern.pattern == "failed"





def test_skip_comments_and_blank_lines(tmp_path):
    # Arrange: mix comments, blanks, and two real rules
    lines = [
        "# this is a comment",
        "",
        "    ",
        f"Event1 {COUNT_FLAG}",
        "",
        "#another comment",
        f"Event2 {LEVEL_FLAG} WARNING"
    ]
    cfg_file = tmp_path / CFG_NAME
    cfg_file.write_text("\n".join(lines) + "\n")

    # Act
    configs = load_configs(str(cfg_file))

    # Assert
    assert len(configs) == 2

    c0 = configs[0]
    assert c0.event_type == "Event1"
    assert c0.count is True
    assert c0.level is None

    c1 = configs[1]
    assert c1.event_type == "Event2"
    assert c1.count is False
    assert c1.level == "WARNING"


def test_empty_or_comments_only(tmp_path):
    cfg = tmp_path / "events.txt"
    # either completely empty:
    cfg.write_text("")
    assert load_configs(str(cfg)) == []

    # or only comment lines:
    cfg.write_text("# just a comment\n# another one\n\n")
    assert load_configs(str(cfg)) == []
