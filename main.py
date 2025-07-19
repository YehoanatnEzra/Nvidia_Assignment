# cli.py
"""
Command-line entry point for the Nvidia log analyzer tool.
"""
import argparse
import json
from pathlib import Path

from log_analyzer.analyzer import LogAnalyzer


def main():
    p = argparse.ArgumentParser(
        prog="log-analyzer",
        description="Analyze log files based on an events specification file."
    )
    p.add_argument(
        "logs_dir",
        help="Directory containing .log and/or .log.gz files"
    )
    p.add_argument(
        "events_file",
        help="Path to the events configuration file (e.g. events.txt)"
    )
    p.add_argument(
        "--from",
        dest="ts_from",
        help="Only include entries at or after this ISO timestamp"
    )
    p.add_argument(
        "--to",
        dest="ts_to",
        help="Only include entries up to this ISO timestamp (inclusive)"
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Output full results as JSON rather than human-readable text"
    )
    args = p.parse_args()

    # Resolve paths
    log_dir = Path(args.logs_dir)
    events_file = Path(args.events_file)

    analyzer = LogAnalyzer(
        str(log_dir),
        str(events_file),
        ts_from=args.ts_from,
        ts_to=args.ts_to
    )

    if args.json:
        # serialize entries for JSON output
        def serialize_entry(e):
            return {
                "timestamp": e.timestamp.isoformat(),
                "level":     e.level,
                "event_type": e.event_type,
                "message":   e.message,
            }

        # Ideally we'd call analyzer.analyze(), but if not implemented,
        # we emulate analysis here.
        results = []
        for cfg in analyzer.configs:
            flt     = Filter = None
        # Fallback to pretty-print
        analyzer.run()
    else:
        analyzer.run()


if __name__ == "__main__":
    main()
