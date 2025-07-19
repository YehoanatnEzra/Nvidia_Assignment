# log_analyzer/analyzer.py
import csv
import gzip
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

from log_analyzer.log_entry import LogEntry
from log_analyzer.event_config import load_configs, EventConfig
from log_analyzer.event_filter import EventFilter


DEFAULT_LOCAL_TIME = "Asia/Jerusalem"


class LogAnalyzer:
    """
    Ties together parsing, configuration, filtering, and reporting.

    Attributes:
        log_dir:       Path to a folder containing log files.
        configs:       list of EventConfig objects
        ts_from:       optional ISO timestamp string (inclusive lower bound)
        ts_to:         optional ISO timestamp string (inclusive upper bound)
    """
    def __init__(self, log_dir: str, events_file: str, ts_from: str | None = None,
                 ts_to: str | None = None, local_timezone: ZoneInfo = ZoneInfo(DEFAULT_LOCAL_TIME)):
        """
        #todo - Should write documentation
        """
        self.log_dir = log_dir
        self.configs: list[EventConfig] = load_configs(events_file)
        self.local_timezone = local_timezone
        self.ts_from = datetime.fromisoformat(ts_from).replace(tzinfo=local_timezone) if ts_from else None
        self.ts_to = datetime.fromisoformat(ts_to).replace(tzinfo=local_timezone) if ts_to else None

    def run(self) -> None:
        for ev_config, matched in self.analyze():
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

    def analyze(self) -> list[tuple[EventConfig, list[LogEntry]]]:
        entries = self._gather_entries()
        results = []
        for ev_config in self.configs:
            flt = EventFilter(ev_config)
            matched = [e for e in entries if flt.matches(e)]
            results.append((ev_config, matched))
        return results

    def _exportable_results(self) -> list[dict]:
        """Return a flat list of log entries for export (used by both JSON and CSV)."""
        entries = []
        for cfg, matched in self.analyze():
            filters = {
                "count": bool(cfg.count),
                "level": cfg.level,
                "pattern": cfg.pattern.pattern if cfg.pattern else None,
            }
            for entry in matched:
                entries.append({
                    "event_type": cfg.event_type,
                    "filters": filters,
                    "timestamp": entry.timestamp.isoformat(),
                    "level": entry.level,
                    "message": entry.message,
                })
        return entries

    def export_to_json(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._exportable_results(), f, indent=2, ensure_ascii=False)

    def export_to_csv(self, path: str) -> None:
        with open(path, "w", newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", "level", "event_type", "message", "filters"])
            writer.writeheader()
            for row in self._exportable_results():
                row["filters"] = str(row["filters"])
                writer.writerow(row)

    def _gather_entries(self) -> list[LogEntry]:
        """
        Walk through all files in log_dir, parse each line to LogEntry,
        apply timestamp range filtering, and collect valid entries.
        """
        entries: list[LogEntry] = []
        for file_name in sorted(os.listdir(self.log_dir)):
            path = os.path.join(self.log_dir, file_name)
            if not os.path.isfile(path):
                continue
            if not (file_name.endswith(".log") or file_name.endswith(".log.gz")):
                continue

            open_func = gzip.open if path.endswith(".gz") else open
            mode = "rt" if path.endswith(".gz") else "r"
            with open_func(path, mode, encoding='utf-8') as f:
                for raw in f:
                    try:
                        entry = LogEntry.parse_line(raw, local_timezone=self.local_timezone)
                    except ValueError:
                        continue  # skip malformed lines

                    if self._in_range(entry):
                        entries.append(entry)
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
