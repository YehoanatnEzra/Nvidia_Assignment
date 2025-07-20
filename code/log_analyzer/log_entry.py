from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from log_analyzer import error_messages

EXPECTED_LINE_FIELDS = 4  # TIMESTAMP, LEVEL, EVENT_TYPE, MESSAGE
MAX_PAST_YEARS = 100  # Logs older than this will be rejected
DEFAULT_TIMEZONE = ZoneInfo("Asia/Jerusalem")  # Default timezone information.


class LogEntry:
    """
    Represents a single log entry.

    Attributes:
       timestamp (datetime): When the event occurred.
       level (str): Log severity (e.g., INFO, WARNING, ERROR).
       event_type (str): Category or type of the event.
       message (str): The textual log message.
    """
    def __init__(self, timestamp: datetime, level: str, event_type: str, message: str):
        """ Initializes a LogEntry instance with timestamp, level, event type, and message. """
        self.timestamp: datetime = timestamp
        self.level: str = level
        self.event_type: str = event_type
        self.message: str = message

    @classmethod
    def parse_line(cls, line: str, local_timezone: ZoneInfo = None) -> "LogEntry":
        """
        Parses a single raw log line into a structured LogEntry object, including validation.

        The log line must follow the format: <TIMESTAMP> <LEVEL> <EVENT_TYPE> <MESSAGE>
        Validation includes:
            - Timestamp in ISO 8601 format
            - Timestamp not in the future
            - Timestamp not older than MAX_PAST_YEARS

        Args:
            line (str): The raw log line to parse.
            local_timezone (ZoneInfo, optional): Timezone to assign if timestamp is naive.

        Returns:
            LogEntry: A validated and parsed LogEntry object.

        Raises:
            ValueError: If the line format is invalid, or if the timestamp is malformed, in the future, or too old.
        """

        if local_timezone is None:
            local_timezone = DEFAULT_TIMEZONE

        # Split into exactly EXPECTED_LINE_FIELDS parts
        parts = line.strip().split(" ", EXPECTED_LINE_FIELDS - 1)

        if len(parts) < EXPECTED_LINE_FIELDS:
            raise ValueError(error_messages.INVALID_LINE_FORMAT)
        ts_str, lvl_str, ev_type, msg = parts

        if not ev_type.isupper() or not lvl_str.isupper():
            raise ValueError(error_messages.INVALID_LINE_FORMAT)

        # Parse ISO8601 timestamp
        try:
            ts = datetime.fromisoformat(ts_str)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=local_timezone)
        except ValueError as e:
            raise ValueError(error_messages.INVALID_TIMESTAMP_FORMAT.format(ts=ts_str, error=e))

        # Validate that the timestamp is not in the future.
        ts = cls._validate_and_parse_timestamp(ts_str, local_timezone)

        return cls(ts, lvl_str, ev_type, msg)

    def __str__(self) -> str:
        """
           Return a human-readable string representation of the log entry.
           Format: <TIMESTAMP> <LEVEL> <EVENT_TYPE> <MESSAGE>
        """
        ts = self.timestamp.isoformat()
        return f"{ts} {self.level} {self.event_type} {self.message}"

    @staticmethod
    def _validate_and_parse_timestamp(ts_str: str, local_timezone: ZoneInfo) -> datetime:
        """
            Parse and validate a timestamp string.

            Ensures ISO format, applies timezone if needed, and verifies the timestamp is neither in the
            future nor too old.
        """
        try:
            ts = datetime.fromisoformat(ts_str)
        except ValueError as e:
            raise ValueError(error_messages.INVALID_TIMESTAMP_FORMAT.format(ts=ts_str, error=e))

        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=local_timezone)

        now = datetime.now(local_timezone)

        if ts > now:
            raise ValueError(error_messages.FUTURE_TIMESTAMP.format(ts=ts, now=now))

        if ts < now - timedelta(days=MAX_PAST_YEARS * 365):
            raise ValueError(error_messages.TOO_OLD_TIMESTAMP.format(ts=ts, years=MAX_PAST_YEARS))

        return ts
