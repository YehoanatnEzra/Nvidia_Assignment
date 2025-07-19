import sys
import gzip
from pathlib import Path
from io import StringIO

import pytest

# adjust this import if your entry-point is named or located differently
from cli import main


def _write_log_file(path, lines, compress=False):
    """Helper to write lines to a log file, optionally gzipped."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if compress:
        with gzip.open(path, 'wt', encoding='utf-8') as f:
            f.write("\n".join(lines))
    else:
        path.write_text("\n".join(lines))


@pytest.fixture(autouse=True)
def add_project_root_to_path(monkeypatch):
    # Ensure `cli` can be imported when tests run from /tests
    proj_root = Path(__file__).parent.parent.resolve()
    monkeypatch.syspath_prepend(str(proj_root))


def test_cli_counts_and_lists(tmp_path, monkeypatch, capsys):
    # 1. Arrange: create a logs folder and events.txt under tmp_path
    logs = tmp_path / "logs"
    config = tmp_path / "events.txt"

    # create two plain entries and one gzipped entry
    _write_log_file(logs / "app.log", [
        "2025-07-18T12:00:00 INFO FooEvent first",
        "2025-07-18T13:00:00 INFO FooEvent second",
    ], compress=False)
    _write_log_file(logs / "app.log.gz", [
        "# this is a comment",
        "2025-07-18T14:00:00 INFO FooEvent third"
    ], compress=True)

    # single rule: count only FooEvent
    config.write_text("FooEvent --count")

    # 2. Act: invoke your CLI via sys.argv
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PYTHONUNBUFFERED", "1")  # if output buffering is an issue
    monkeypatch.setattr(sys, "argv", ["cli.py", "logs", "events.txt"])
    main()  # call the entry-point

    # 3. Assert: capture and examine stdout
    captured = capsys.readouterr().out
    assert "FooEvent: 3 matches" in captured


def test_cli_list_mode(tmp_path, monkeypatch, capsys):
    # Test the default (no --count) listing behavior
    logs = tmp_path / "logs"
    config = tmp_path / "events.txt"
    _write_log_file(logs / "a.log", ["2025-07-18T12:00:00 INFO BarEvent hey"], compress=False)
    config.write_text("BarEvent")  # no --count

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["cli.py", "logs", "events.txt"])
    main()

    out = capsys.readouterr().out
    assert "BarEvent matching entries:" in out
    assert "2025-07-18T12:00:00 INFO BarEvent hey" in out
