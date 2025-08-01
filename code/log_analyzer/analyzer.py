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
from log_analyzer import error_messages
from functools import cached_property

DEFAULT_LOCAL_TIME = "Asia/Jerusalem"    # Default timezone used for interpreting timestamps
MAX_WORKERS = os.cpu_count() or 4        # Maximum number of threads to use


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
        try:
            self.ts_from = datetime.fromisoformat(ts_from).replace(tzinfo=local_timezone) if ts_from else None
        except ValueError as e:
            raise ValueError(error_messages.INVALID_TIMESTAMP_FORMAT.format(ts=ts_from, error=e))

        try:
            self.ts_to = datetime.fromisoformat(ts_to).replace(tzinfo=local_timezone) if ts_to else None
        except ValueError as e:
            raise ValueError(error_messages.INVALID_TIMESTAMP_FORMAT.format(ts=ts_to, error=e))

        self.max_workers = MAX_WORKERS

    # -------------------
    # Helper Functions
    # -------------------

    @cached_property
    def _cached_analysis(self) -> list[tuple[EventConfig, list[LogEntry]]]:
        """Computes the filtered log entries per event config once and caches the result."""
        return self._analyze()

    def _analyze(self) -> list[tuple[EventConfig, list[LogEntry]]]:
        """ Analyze log entries by applying all event filters in parallel using threads."""
        entries = self._gather_entries()  # Load and filter log entries from all log files

        def _process_config(ev_config: EventConfig) -> tuple[EventConfig, list[LogEntry]]:
            """ A task that filters entries using a specific config"""
            flt = EventFilter(ev_config)
            matched = [e for e in entries if flt.matches(e)]
            return ev_config, matched

        results = []
        # Use thread pool to process each config in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(_process_config, cfg): cfg for cfg in self.configs}
            # Collect results as each thread finishes
            for future in as_completed(futures):
                results.append(future.result())

        return results

    def _gather_entries(self) -> list[LogEntry]:
        """
         Walks through all log files in the log directory and parses them into LogEntry objects, using threads to
         process multiple files concurrently.
        """
        # Identify valid log files: .log or .gz
        entries: list[LogEntry] = []
        log_dir_path = Path(self.log_dir)
        log_files = [p for p in log_dir_path.iterdir() if p.is_file() and (p.suffix == ".log" or p.suffix == ".gz")]

        def _process_file(path: Path) -> list[LogEntry]:
            """
            Reads a single log file, parses each line to a LogEntry (if valid),and applies time-range filtering.
            """
            result = []
            open_func = gzip.open if path.suffix == ".gz" else open
            with open_func(path, "rt", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    try:
                        entry = LogEntry.parse_line(line, local_timezone=self.local_timezone)
                        if entry and self._in_range(entry):
                            result.append(entry)
                    except ValueError:
                        continue   # Skip lines that don't match expected format.
            return result

        # Process all files in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(_process_file, path): path for path in log_files}
            for future in as_completed(futures):
                entries.extend(future.result())

        return entries

    def _in_range(self, entry: LogEntry) -> bool:
        """Check whether entry.timestamp is between self.ts_from and self.ts_to (inclusive)."""
        ts = entry.timestamp
        if self.ts_from and ts < self.ts_from:
            return False
        if self.ts_to and ts > self.ts_to:
            return False
        return True

    # -------------------
    # Public Functions
    # -------------------
    def run(self) -> None:
        """
        Executes the full log analysis pipeline and prints the results to the console.

        For each event configuration (from the config file), this method:
            - Analyzes matching entries from all logs
            - Applies the relevant filters (event_type, --level, --pattern)
            - Prints a header that describes the filters
            - If --count was specified, prints the number of matches
            - Otherwise, prints the actual matching log entries (or "(none)" if there are none)

        This is the main method triggered in CLI usage when no export format is requested.
        """

        for ev_config, matched in self._cached_analysis:
            header = f"EventType: {ev_config.event_type}"
            specs = []
            if ev_config.count:
                specs.append("v count")
            if ev_config.level:
                specs.append(f" level={ev_config.level}")
            if ev_config.pattern:
                specs.append(f" pattern={ev_config.pattern.pattern}")
            if specs:
                header += "\nflags:" + ",".join(specs) + ":"

            if ev_config.count:
                print(f"{header}\nCount of matches: {len(matched)}\n")
            else:
                print(f"{header}\nmatching entries:")
                for entry in matched:
                    print(f"  {entry}")
                if not matched:
                    print("  none")
                print(" ")

    def export_to_json(self, path: str) -> None:
        """
             Exports filtered log entries to a JSON file.

             Args:
                 path (str): Destination file path.
             """
        with open(path, "w", encoding="utf-8") as f:
            results = []
            for ev_config, matched in self._cached_analysis:
                group = {
                    "event_type": ev_config.event_type,
                    "filters": {
                        "count": ev_config.count,
                        "level": ev_config.level,
                        "pattern": ev_config.pattern.pattern if ev_config.pattern else None,
                    },
                    "entries": [
                        {
                            "timestamp": entry.timestamp.isoformat(),
                            "level": entry.level,
                            "message": entry.message,
                        }
                        for entry in matched
                    ]
                }
                results.append(group)

            with open(path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

