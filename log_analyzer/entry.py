# TODO - better documentation
"""Log parser module.
This module provides utilities to parse log entries from text lines into structured LogEntry objects.
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


EXPECTED_LINE_FIELDS = 4  # Number of fields we expect when splitting a log line.
MAX_PAST_YEARS = 100 # Maximum allowed age for a timestamp (in years) before we consider it "too old".
LOCAL_TIMEZONE = ZoneInfo('America/New_York') # Timezone for interpreting and validating timestamps.

class LogEntry:
    """Represents a single log entry.
       Attributes:
           timestamp (datetime): When the event occurred.
           level (str): Log severity (e.g., INFO, WARNING, ERROR).
           event_type (str): Category or type of the event.
           message (str): The textual log message.
       """
    #todo - check if timestamp is valid (format and not is the future or to much time before)
    def __init__(self, timestamp: datetime, level:str,event_type:str, message:str):
        self.timestamp = timestamp
        self.level = level
        self.event_type = event_type
        self.message = message

        @classmethod
        def parse_line(cls, line: str) -> "LogEntry":
            """
             Parse a single log line into a LogEntry, validating the timestamp.
            :param cls:
            :param line:
            :return:
            """
            # Split into exactly EXPECTED_LINE_FIELDS parts
            parts = line.strip().split(" ", EXPECTED_LINE_FIELDS - 1)
            if len(parts) < EXPECTED_LINE_FIELDS:
                raise ValueError(f"Line doesn’t have 4 parts: {line!r}")
            ts_str, lvl_str, ev_type, msg = parts

           # Parse ISO8601 timestamp
            try:
                ts = datetime.fromisoformat(ts_str)
            except ValueError:
                raise ValueError(f"Invalid timestamp: {ts_str!r}") # todo  - should i handle better error message

            #    Use your local zone if your logs are in Asia/Jerusalem
            now = datetime.now(LOCAL_TIMEZONE)

            #  Validate against “now” in your local timezone
            if ts > now:
                raise ValueError(
                    f"Timestamp {ts.isoformat()} is in the future (now={now.isoformat()})"
                )
            if ts < now - timedelta(days=MAX_PAST_YEARS * 365):
                raise ValueError(
                    f"Timestamp {ts.isoformat()} is more than "
                    f"{MAX_PAST_YEARS} years old")

            return cls(ts, level, event_type, message)