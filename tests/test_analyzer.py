import gzip
import sys
from datetime import datetime
from io import StringIO

import pytest

from log_analyzer.analyzer import LogAnalyzer


def _write_log_file(path, lines, compress=False):
    """ Helper to write lines to a log file, optionally gzipped."""
    if compress:
        with gzip.open(path, 'wt', encoding='utf-8') as f:
            f.write("\n".join(lines))
    else:
        path.write_text("\n".join(lines))


def test_run_with_empty_log_folder(tmp_path):
    """
      Verify that the analyzer handles an empty log folder without errors,
       and returns zero matches as expected.
    """
    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    config_file = tmp_path / "events.txt"
    config_file.write_text("TELEMETRY --count")

    saved_stdout = sys.stdout
    try:
        sys.stdout = StringIO()
        analyzer = LogAnalyzer(str(log_dir), str(config_file))
        analyzer.run()
        output = sys.stdout.getvalue()

        assert "TELEMETRY" in output
        assert "Count of matches: 0" in output
    finally:
        sys.stdout = saved_stdout


def test_run_prints_expected_output(tmp_path):
    """
    Ensure the analyzer skips invalid log lines, comment lines in both logs and config,
    and correctly counts only valid matching entries from both .log and .log.gz files.
    """

    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    l1_valid1 = "2025-07-18T12:00:00 INFO TESTEVENT Hello world"
    l1_invalid1 = "this is invalid log line"
    _write_log_file(log_dir / "l1.log", [l1_valid1, l1_invalid1], compress=False)

    l2_valid1 = "2025-07-18T13:00:00 INFO TESTEVENT Another entry"
    l2_comment1 = "# 2025-07-18T13:00:00 INFO TESTEVENT Another entry"
    l2_valid2 = "2025-07-18T13:00:00 INFO TESTEVENT another text"
    l2_invalid1 = "this is invalid log line 2"
    l2_invalid2 = "invalid3"
    _write_log_file(log_dir / "l2.log.gz", [l2_valid1, l2_comment1, l2_invalid1, l2_invalid2, l2_valid2], compress=True)

    # Config that matches the event type and counts
    config_file = tmp_path / "events.txt"
    config_file.write_text("# comment \n TESTEVENT --count")

    # Redirect stdout to capture print output
    saved_stdout = sys.stdout
    try:
        out = StringIO()
        sys.stdout = out

        analyzer = LogAnalyzer(str(log_dir), str(config_file))
        analyzer.run()

        output = out.getvalue()

        assert "TESTEVENT" in output
        assert "Count of matches: 3" in output
    finally:
        sys.stdout = saved_stdout


def test_invalid_config_line_raises_error(tmp_path):
    """ Test that an invalid config line raises a ValueError with a proper message."""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    config_file = tmp_path / "events.txt"
    config_file.write_text("invalid config line\n")

    with pytest.raises(ValueError) as excinfo:
        LogAnalyzer(str(log_dir), str(config_file))
    assert "Invalid flag" in str(excinfo.value)


def test_run_with_timestamp_range_filter(tmp_path):
    """
    Verify timestamp filtering behavior:
    'ts_from' is exclusive (entries with the exact same timestamp should be excluded),
    'ts_to' is inclusive (entries with the exact same timestamp should be included).
    """

    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    ts_from = "2025-07-18T00:00:00"
    ts_to = "2025-07-18T23:59:50"

    early1 = "2025-07-17T10:00:00 INFO EVENT msg early"
    middle1 = f"{ts_from} INFO EVENT msg inside"   # inclusive upper bound
    middle2 = "2025-07-18T12:00:00 INFO EVENT msg inside"
    middle3 = "2025-07-18T12:10:00 INFO EVENT msg inside"
    middle4 = f"{ts_to} INFO EVENT msg inside"  # inclusive lower bound
    late1 = "2025-07-18T23:59:52 INFO EVENT msg late"
    late2 = "2025-07-19T20:00:00 INFO EVENT msg late"

    _write_log_file(log_dir / "range.log", [early1, middle1, middle2, middle3, late1, late2, middle4], compress=False)

    config_file = tmp_path / "events.txt"
    config_file.write_text("EVENT --count")

    saved_stdout = sys.stdout
    try:
        sys.stdout = StringIO()
        analyzer = LogAnalyzer(str(log_dir), str(config_file), ts_from, ts_to)
        analyzer.run()
        output = sys.stdout.getvalue()

        assert "EVENT" in output
        assert "Count of matches: 4" in output

    finally:
        sys.stdout = saved_stdout


def test_multiple_filters_for_same_event_type(tmp_path):
    """
    Ensure that multiple filters for the same event type (e.g., --count, --pattern, --level)
    are each evaluated and reported independently.
    """

    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    log_lines = [
        "2025-07-18T10:00:00 INFO EVENT First valid match",
        "2025-07-18T11:00:00 INFO EVENT Another valid match",
        "2025-07-18T12:00:00 DEBUG EVENT Should not match level INFO",
        "2025-07-18T13:00:00 INFO OTHER Should be ignored"
    ]
    _write_log_file(log_dir / "test.log", log_lines)

    config_lines = [
        "EVENT --count",
        "EVENT  --pattern ^Another.*",
        "EVENT --count --level INFO"
    ]
    config_file = tmp_path / "events.txt"
    config_file.write_text("\n".join(config_lines))

    saved_stdout = sys.stdout
    try:
        sys.stdout = StringIO()
        LogAnalyzer(str(log_dir), str(config_file)).run()

        output = sys.stdout.getvalue()
        assert "Count of matches: 3" in output
        assert "^Another.*" in output
        assert "Count of matches: 2" in output
    finally:
        sys.stdout = saved_stdout
