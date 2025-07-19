# cli.py
"""
Command-line entry point for the log analyzer tool.
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path


from log_analyzer.analyzer import LogAnalyzer


def _print_intro():
    print("\nHi! Welcome to the Log Analyzer :)")
    print("-----------------------------------------")
    print("I'm now scanning your logs and applying filters based on your configuration\nLet’s get started!\n")


def _print_outro():
    print("\nThank you, have a nice day :) \n")


def _handle_export(analyzer):
    choice = input("Would you like to export the results? Type 'json', 'csv', or 'n' for no export. ").strip().lower()

    while choice not in ("json", "csv", "n"):
        choice = input("Invalid option. Please type 'json', 'csv', or 'n': ").strip().lower()

    if choice != "n":
        date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"log_output_{date_str}.{choice}"
        if choice == "json":
            analyzer.export_to_json(filename)
        elif choice == "csv":
            analyzer.export_to_csv(filename)
        print(f"Export complete: {filename}\n")


def main():
    p = argparse.ArgumentParser(
        prog="log-analyzer",
        description="Analyze log files based on an events specification file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    p.add_argument("logs_dir", help="Directory containing .log and/or .log.gz files")
    p.add_argument("events_file", help="Path to the events configuration file (e.g. events.txt)")
    p.add_argument("--from", dest="ts_from", help="Only include entries at or after this ISO timestamp")
    p.add_argument("--to", dest="ts_to", help="Only include entries up to this ISO timestamp (inclusive)")
    args = p.parse_args()

    # Resolve paths
    log_dir = Path(args.logs_dir)
    events_file = Path(args.events_file)

    _print_intro()
    try:
        analyzer = LogAnalyzer(str(log_dir), str(events_file), ts_from=args.ts_from, ts_to=args.ts_to)
    except ValueError as e:
        print(f"\n{e}")
        sys.exit(1)
    analyzer.run()
    _handle_export(analyzer)
    _print_outro()


if __name__ == "__main__":
    main()
