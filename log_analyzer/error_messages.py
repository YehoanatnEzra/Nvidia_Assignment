"""
Standardized error messages used throughout the log_analyzer system.
"""

# Raised when a log line doesn't follow the expected structure or formatting
INVALID_LINE_FORMAT = (
    "Invalid log line format — expected format: <TIMESTAMP> <LEVEL> <EVENT_TYPE> <MESSAGE>. "
    "LEVEL and EVENT_TYPE must be uppercase. "
    "TIMESTAMP must be ISO‑8601 (YYYY‑MM‑DDThh:mm:ss), "
    "Example: 2025-07-17T12:00:00 INFO LOGIN User 'bob' logged in"
)

# Raised when a timestamp string cannot be parsed
INVALID_TIMESTAMP_FORMAT = (
    "Invalid timestamp format: {ts!r}. "
    "Expected format: YYYY-MM-DDTHH:MM:SS (e.g. 2025-06-01T14:03:05). Error: {error}"
)

# Raised when a timestamp is in the future
FUTURE_TIMESTAMP = (
    "Timestamp {ts} is in the future (now={now})"
)

# Raised when a timestamp is older than the allowed limit
TOO_OLD_TIMESTAMP = (
    "Timestamp {ts} is too old — more than {years} years ago"
)

# Raised when a flag is used without a value
MISSING_VALUE_ERR = (
    "Missing value for {flag!r} in line: {line!r}"
)

# Raised when an unsupported flag is used in the config
INVALID_FLAG = (
    "Invalid flag {flag!r} in config line {line!r}. "
    "Allowed flags are: {allowed}."
)
