"""
 message.py — Centralized user-facing messages for CLI output and error reporting.
"""

# Prints a  welcome message at the beginning of the analysis.
INTRO_MSG = (
    "\nHi! Welcome to the Log Analyzer :)\n"
    "-----------------------------------------\n"
    "I'm now scanning your logs and applying filters based on your configuration\nLet’s get started!\n"
)

# Prints a closing thank-you message after the analysis is complete.
OUTRO_MSG = "\nThank you, have a nice day :) \n"

# Error displayed when the logs directory path does not exist or is not a directory.
LOGS_DIR_NOT_FOUND = "\nlogs directory not found or is not a directory :(\n"

# Error displayed when the events configuration file path does not exist or is not a file.
EVENTS_FILE_NOT_FOUND = "\nEvents configuration file not found :(\n"


EXPORT_QUESTION = "Would you like to export the results?\n"
