# log_analyzer/analyzer.py
import csv
import gzip
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from log_analyzer.log_entry import LogEntry
from log_analyzer.event_config import load_configs, EventConfig
from log_analyzer.event_filter import EventFilter
from concurrent.futures import ThreadPoolExecutor, as_completed


DEFAULT_LOCAL_TIME = "Asia/Jerusalem"
MAX_WORKERS = os.cpu_count() or 4


class LogAnalyzer:
    """
    Ties together parsing, configuration, filtering, and reporting.

    Attributes:
        log_dir:       Path to a folder containing log files.
        configs:       list of EventConfig objects
        ts_from:       optional ISO timestamp string (inclusive lower bound)
        ts_to:         optional ISO timestamp string (inclusive upper bound)
        local_timezone (ZoneInfo): The timezone used for interpreting timestamps.
    """
    def __init__(self, log_dir: str, events_file: str, ts_from: str | None = None,
                 ts_to: str | None = None, local_timezone: ZoneInfo = ZoneInfo(DEFAULT_LOCAL_TIME)):
        """
        Initializes the LogAnalyzer.

        Args:
            log_dir (str): Directory containing log files (.log or .log.gz).
            events_file (str): Path to a file specifying event filter configurations.
            ts_from (str | None): Optional ISO timestamp string for the start of the time range.
            ts_to (str | None): Optional ISO timestamp string for the end of the time range.
            local_timezone (ZoneInfo): Timezone to apply to parsed timestamps.
        """
        self.log_dir = log_dir
        self.configs: list[EventConfig] = load_configs(events_file)
        self.local_timezone = local_timezone
        self.ts_from = datetime.fromisoformat(ts_from).replace(tzinfo=local_timezone) if ts_from else None
        self.ts_to = datetime.fromisoformat(ts_to).replace(tzinfo=local_timezone) if ts_to else None
        self.max_workers = MAX_WORKERS

    def _analyze(self) -> list[tuple[EventConfig, list[LogEntry]]]:
        """
        Analyze log entries by applying all event filters in parallel using threads.
        """
        entries = self._gather_entries()

        def process_config(ev_config: EventConfig) -> tuple[EventConfig, list[LogEntry]]:
            flt = EventFilter(ev_config)
            matched = [e for e in entries if flt.matches(e)]
            return (ev_config, matched)

        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(process_config, cfg): cfg for cfg in self.configs}
            for future in as_completed(futures):
                results.append(future.result())

        return results

    def _gather_entries(self) -> list[LogEntry]:
        """
        Parallel version: Walk through all files in log_dir using threads,
        parse each line to LogEntry, apply timestamp filtering, and collect valid entries.
        """
        entries: list[LogEntry] = []
        log_dir_path = Path(self.log_dir)
        log_files = [
            p for p in log_dir_path.iterdir()
            if p.is_file() and (p.suffix == ".log" or p.suffix == ".gz")
        ]

        def _process_file(path: Path) -> list[LogEntry]:
            result = []
            open_func = gzip.open if path.suffix == ".gz" else open
            with open_func(path, "rt", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    entry = LogEntry.parse_line(line, local_timezone=self.local_timezone)
                    if entry and self._in_range(entry):
                        result.append(entry)
            return result

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(_process_file, path): path for path in log_files}
            for future in as_completed(futures):
                entries.extend(future.result())

        return entries

    def _in_range(self, entry: LogEntry) -> bool:
        """
        Check whether entry.timestamp is between self.ts_from and self.ts_to (inclusive).
        If no bounds are set, always True.
        """
        ts = entry.timestamp
        if self.ts_from and ts < self.ts_from:
            return False
        if self.ts_to and ts > self.ts_to:
            return False
        return True

    def _exportable_results(self) -> list[dict]:
        """Return a flat list of log entries for export (used by both JSON and CSV)."""
        entries = []
        for ev_confing, matched in self._analyze():
            filters = {
                "count": bool(ev_confing.count),
                "level": ev_confing.level,
                "pattern": ev_confing.pattern.pattern if ev_confing.pattern else None,
            }
            for entry in matched:
                entries.append({
                    "event_type": ev_confing.event_type,
                    "filters": filters,
                    "timestamp": entry.timestamp.isoformat(),
                    "level": entry.level,
                    "message": entry.message,
                })
        return entries

    def run(self) -> None:
        for ev_config, matched in self._analyze():
            header = f"EventType: {ev_config.event_type}"
            specs = []
            if ev_config.count:
                specs.append("count")
            if ev_config.level:
                specs.append(f"level={ev_config.level}")
            if ev_config.pattern:
                specs.append(f"pattern={ev_config.pattern.pattern}")
            if specs:
                header += "\nflags:" + ",".join(specs) + ":"

            if ev_config.count:
                print(f"{header}\nCount of matches: {len(matched)}\n")
            else:
                print(f"{header}\nmatching entries:")
                for entry in matched:
                    print(f"  {entry}")
                if not matched:
                    print("  (none)")
                print(" ")

    def export_to_json(self, path: str) -> None:
        """
             Exports filtered log entries to a JSON file.

             Args:
                 path (str): Destination file path.
             """
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._exportable_results(), f, indent=2, ensure_ascii=False)

    def export_to_csv(self, path: str) -> None:
        """
              Exports filtered log entries to a CSV file.

              Args:
                  path (str): Destination file path.
              """
        with open(path, "w", newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "level", "event_type", "message", "filters"])
            writer.writeheader()
            for row in self._exportable_results():
                row["filters"] = str(row["filters"])
                writer.writerow(row)
