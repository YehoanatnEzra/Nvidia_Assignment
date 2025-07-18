# errors.py

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
