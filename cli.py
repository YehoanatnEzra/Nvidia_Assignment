# cli.py
"""
Command-line entry point for the log analyzer tool.
"""
import argparse
import csv
import json
from datetime import datetime
from pathlib import Path


from log_analyzer.analyzer import LogAnalyzer


def _print_intro():
    print("\nHi there! Welcome to the Log Analyzer :)")
    print("-----------------------------------------")
    print("We're now scanning your logs and applying filters based on your configuration...\nLet’s get started!\n")


def _print_outro():
    print("Done! Log analysis complete.\n")


def _handle_export(analyzer):
    choice = input("Would you like to export the results? Type 'json', 'csv', or 'n' for no export. ").strip().lower()
    while choice not in ("json", "csv", "n"):
        print(" Sorry, Invalid option. Please 'json', 'csv', or 'n' for no export.\n")
        choice = (
            input("Would you like to export the results? Type 'json', 'csv', or 'n' for no export. ").strip().lower())

    if choice == "n":
        print("No export performed.\n See you next time\n")
        return

    if choice == "json":
        analyzer.export_json()
    elif choice == "csv":
        analyzer.export_csv()








def main():
    p = argparse.ArgumentParser(
        prog="log-analyzer",
        description="Analyze log files based on an events specification file."
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

    analyzer = LogAnalyzer(str(log_dir), str(events_file), ts_from=args.ts_from, ts_to=args.ts_to)
    analyzer.run()

    _print_outro()
    #_handle_export(analyzer)


if __name__ == "__main__":
    main()
