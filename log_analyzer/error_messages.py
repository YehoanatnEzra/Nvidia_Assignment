
INVALID_LINE_FORMAT = (
    "Invalid log line format — expected format: <TIMESTAMP> <LEVEL> <EVENT_TYPE> <MESSAGE>. "
    "LEVEL and EVENT_TYPE must be uppercase. "
    "TIMESTAMP must be ISO‑8601 (YYYY‑MM‑DDThh:mm:ss), "
    "Example: 2025-07-17T12:00:00 INFO LOGIN User 'bob' logged in"
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