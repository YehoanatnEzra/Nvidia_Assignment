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
        assert "0 matches" in output
    finally:
        sys.stdout = saved_stdout


def test_run_prints_expected_output(tmp_path):
    """
    Ensure the analyzer skips invalid log lines, comment lines in both logs and config,
    and correctly counts only valid matching entries from both .log and .log.gz files.
    """

    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    l1_valid1 = "2025-07-18T12:00:00 INFO TestEvent Hello world"
    l1_invalid1 = "this is invalid log line"
    _write_log_file(log_dir / "l1.log", [l1_valid1, l1_invalid1], compress=False)

    l2_valid1 = "2025-07-18T13:00:00 INFO TestEvent Another entry"
    l2_comment1 = "# 2025-07-18T13:00:00 INFO TestEvent Another entry"
    l2_valid2 = "2025-07-18T13:00:00 INFO TestEvent another text"
    l2_invalid1 = "this is invalid log line 2"
    l2_invalid2 = "invalid3"
    _write_log_file(log_dir / "l2.log.gz", [l2_valid1, l2_comment1, l2_invalid1, l2_invalid2, l2_valid2], compress=True)

    # Config that matches the event type and counts
    config_file = tmp_path / "events.txt"
    config_file.write_text("# comment \n TestEvent --count")

    # Redirect stdout to capture print output
    saved_stdout = sys.stdout
    try:
        out = StringIO()
        sys.stdout = out

        analyzer = LogAnalyzer(str(log_dir), str(config_file))
        analyzer.run()

        output = out.getvalue()

        assert "TestEvent" in output
        assert "3 matches" in output
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

    early1 = "2025-07-17T10:00:00 INFO EventType msg early"
    middle1 = f"{ts_from} INFO EventType msg inside"   # inclusive upper bound
    middle2 = "2025-07-18T12:00:00 INFO EventType msg inside"
    middle3 = "2025-07-18T12:10:00 INFO EventType msg inside"
    late1 = f"{ts_to} INFO EventType msg inside"  # exclusive lower bound
    late2 = "2025-07-18T23:59:52 INFO EventType msg late"
    late3 = "2025-07-19T20:00:00 INFO EventType msg late"

    _write_log_file(log_dir / "range.log", [early1, middle1, middle2, middle3, late1, late2, late3], compress=False)

    config_file = tmp_path / "events.txt"
    config_file.write_text("EventType --count")

    saved_stdout = sys.stdout
    try:
        sys.stdout = StringIO()
        analyzer = LogAnalyzer(str(log_dir), str(config_file), ts_from, ts_to)
        analyzer.run()
        output = sys.stdout.getvalue()

        assert "EventType" in output
        assert "3 matches" in output
        
    finally:
        sys.stdout = saved_stdout
