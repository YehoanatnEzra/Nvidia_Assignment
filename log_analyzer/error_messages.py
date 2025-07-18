# error_messages.py

INVALID_LINE_FORMAT = (
    "Invalid log line format — expected format: <TIMESTAMP> <LEVEL> <EVENT_TYPE> <MESSAGE>"
)

INVALID_TIMESTAMP_FORMAT = (
    "Invalid timestamp format: {ts!r}. "
    "Expected format: YYYY-MM-DDTHH:MM:SS (e.g. 2025-06-01T14:03:05). Error: {error}"
)

FUTURE_TIMESTAMP = (
    "Timestamp {ts} is in the future (now={now})"
)

TOO_OLD_TIMESTAMP = (
    "Timestamp {ts} is too old — more than {years} years ago"
)

# Raised when a flag requires a value but none was provided
MISSING_VALUE_ERR = (
    "Missing value for {flag!r} in line: {line!r}"
)

# Raised when an unknown flag is encountered
INVALID_FLAG = (
    "Invalid flag {flag!r} in config line {line!r}. "
    "Allowed flags are: {allowed}."
)