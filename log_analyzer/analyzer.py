# log_analyzer/analyzer.py

import os
from datetime import datetime, timezone

from log_analyzer.log_entry import LogEntry
from log_analyzer.event_config import load_configs, EventConfig
from log_analyzer.event_filter import EventFilter


class LogAnalyzer:
    """
    Ties together parsing, configuration, filtering, and reporting.

    Attributes:
        log_dir:       directory containing log files (text files)
        configs:       list of EventConfig objects
        ts_from:       optional ISO timestamp string (inclusive lower bound)
        ts_to:         optional ISO timestamp string (inclusive upper bound)
    """
    def __init__(
        self,
        log_dir: str,
        events_file: str,
            ts_from: str | None = None,
            ts_to: str | None = None,

    ):
        self.log_dir = log_dir
        self.configs: list[EventConfig] = load_configs(events_file)
        self.ts_from = datetime.fromisoformat(ts_from) if ts_from else None
        self.ts_to = datetime.fromisoformat(ts_to) if ts_to else None

    def run(self) -> None:
        """
        Execute the analysis: parse logs, apply filters, and print results.
        Prints either counts or matching entries based on each EventConfig.
        """
        entries = self._gather_entries()
        for cfg in self.configs:
            flt = EventFilter(cfg)
            matched = [e for e in entries if flt.matches(e)]

            header = f"[{cfg.event_type}]"
            if cfg.count:
                print(f"{header} {len(matched)} matches")
            else:
                print(f"{header} matching entries:")
                for e in matched:
                    print(f"  {e}")
                if not matched:
                    print("  (none)")

    def _gather_entries(self) -> List[LogEntry]:
        """
        Walk through all files in log_dir, parse each line to LogEntry,
        apply timestamp range filtering, and collect valid entries.
        """
        entries: List[LogEntry] = []
        for fname in sorted(os.listdir(self.log_dir)):
            path = os.path.join(self.log_dir, fname)
            if not os.path.isfile(path):
                continue
            with open(path, 'r', encoding='utf-8') as f:
                for raw in f:
                    try:
                        entry = LogEntry.parse_line(raw)
                    except ValueError:
                        # skip malformed lines
                        continue
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
