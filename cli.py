"""
cli.py — Command-line interface for the Log Analyzer Tool

This script serves as the main entry point for running the Log Analyzer, a command-line utility that
 scans log files, filters events based on user-defined rules, and reports the results.

Usage:
    python cli.py <logs_dir> <events_file> [--from <timestamp>] [--to <timestamp>]

Arguments:
    logs_dir: (str): Path to the directory containing '.log' or '.log.gz' files.
    events_file: (str): Path to the events configuration file (e.g., events.txt).
    --from (str, optional): ISO-8601 formatted lower timestamp bound (inclusive).
    --to (str, optional): ISO-8601 formatted upper timestamp bound (inclusive).

Features:
    - Supports multiple filters per event (type, log level, regex pattern).
    - Can output either raw matching entries or a count summary.
    - Interactive option to export results as JSON.
    - Handles both plain text logs (.log) and compressed logs (.log.gz).

Author:
    Yehonatan Ezra - yonzra12@gmail.com
    Created as part of the NVIDIA Home Assignment.
"""

import argparse
from datetime import datetime
from pathlib import Path
from log_analyzer.analyzer import LogAnalyzer
import messages


# -------------------
# Helper Functions
# -------------------


def _handle_export(analyzer):
    """
    Interactively prompts the user to export the analysis results.
    If the user selects 'json' or 'csv', the results are written to a timestamped file.
    """
    print(messages.EXPORT_QUESTION)
    choice = ""
    while choice not in ("y", "n"):
        choice = input("Please type 'y' or 'n': ").strip().lower()

    if choice == "y":
        date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"log_output_{date_str}.json"
        analyzer.export_to_json(filename)
        print(f"Export complete: {filename}\n")


# -------------------
# Main Function
# -------------------


def main():
    """
    Entry point of the CLI tool.

    Parses command-line arguments, initializes the LogAnalyzer instance,
    runs the analysis, optionally exports the results, and prints intro/outro messages.

    Exits with status code 1 if the LogAnalyzer fails to initialize due to bad input.
    """
    # Set up argument parser for command-line input
    p = argparse.ArgumentParser(
        prog="log-analyzer",
        description="Analyze log files based on an events specification file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    p.add_argument("logs_dir", help="Directory containing .log and/or .log.gz files")
    p.add_argument("events_file", help="Path to the events configuration file (e.g. events.txt)")
    p.add_argument("--from", dest="ts_from", help="Only include entries at or after this ISO timestamp")
    p.add_argument("--to", dest="ts_to", help="Only include entries up to this ISO timestamp (inclusive)")

    # Parse the command-line arguments into a namespace
    args = p.parse_args()

    # Resolve paths
    log_dir = Path(args.logs_dir)
    events_file = Path(args.events_file)
    if not log_dir.exists() or not log_dir.is_dir():
        print(messages.LOGS_DIR_NOT_FOUND)
        return

    if not events_file.exists() or not events_file.is_file():
        print(messages.EVENTS_FILE_NOT_FOUND)
        return

    print(messages.INTRO_MSG) # welcome message

    analyzer = LogAnalyzer(str(log_dir), str(events_file), ts_from=args.ts_from, ts_to=args.ts_to)
    analyzer.run()  # Run the core analysis: read logs, apply filters, and print results

    # Ask the user if they want to export the results to Json
    _handle_export(analyzer)

    print(messages.OUTRO_MSG)  # Show closing message


if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        print(f"{e}\n")
        print("Please try again :)")
