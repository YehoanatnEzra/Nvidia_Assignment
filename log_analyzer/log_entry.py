from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from log_analyzer import error_messages

EXPECTED_LINE_FIELDS = 4  # Number of fields we expect when splitting a log line.
MAX_PAST_YEARS = 100  # Maximum allowed age for a timestamp (in years) before we consider it "too old".
DEFAULT_TIMEZONE = ZoneInfo("Asia/Jerusalem")  # Default timezone information.


class LogEntry:
    """Represents a single log entry.
       Attributes:
           timestamp (datetime): When the event occurred.
           level (str): Log severity (e.g., INFO, WARNING, ERROR).
           event_type (str): Category or type of the event.
           message (str): The textual log message.
       """

    def __init__(self, timestamp: datetime, level: str, event_type: str, message: str):
        """
           Initializes a LogEntry instance with timestamp, level, event type, and message.
           """
        self.timestamp = timestamp
        self.level = level
        self.event_type = event_type
        self.message = message

    @classmethod
    def parse_line(cls, line: str, local_timezone: ZoneInfo = None) -> "LogEntry":
        """
        parses a single raw log line into a structured LogEntry object.
        including validation of the timestamp format and range.
        The log line must follow the format: <TIMESTAMP> <LEVEL> <EVENT_TYPE> <MESSAGE>
        The timestamp must: Be in ISO 8601 format, not be in the future and not be before than MAX_PAST_YEARS years.

        Args:
            line (str): The raw log line to parse.
            local_timezone (ZoneInfo, optional): Timezone to assign if timestamp is naive.

        Returns:
             LogEntry: A validated and parsed LogEntry object.

        Raises:
             ValueError: If the line format is invalid, or if the timestamp is malformed, in the future or too old.
        """
        if local_timezone is None:
            local_timezone = DEFAULT_TIMEZONE

        # Split into exactly EXPECTED_LINE_FIELDS parts
        parts = line.strip().split(" ", EXPECTED_LINE_FIELDS - 1)

        if len(parts) < EXPECTED_LINE_FIELDS:
            raise ValueError(error_messages.INVALID_LINE_FORMAT)
        ts_str, lvl_str, ev_type, msg = parts

        # Parse ISO8601 timestamp
        try:
            ts = datetime.fromisoformat(ts_str)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=local_timezone)
        except ValueError as e:
            raise ValueError(error_messages.INVALID_TIMESTAMP_FORMAT.format(ts=ts_str, error=e))

        now = datetime.now(local_timezone)

        # Validate that the timestamp is not in the future.
        if ts > now:
            raise ValueError(error_messages.FUTURE_TIMESTAMP.format(ts=ts, now=now))

        # Validate that the timestamp is not unreasonably old.
        if ts < now - timedelta(days=MAX_PAST_YEARS * 365):
            raise ValueError(error_messages.TOO_OLD_TIMESTAMP.format(ts=ts, years=MAX_PAST_YEARS))

        return cls(ts, lvl_str, ev_type, msg)

    def __str__(self) -> str:
        ts = self.timestamp.isoformat()
        return f"{ts} {self.level} {self.event_type} {self.message}"

