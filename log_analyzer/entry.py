# log_analyzer/entry.py

from datetime import datetime

class LogEntry:
    #todo - check if timestamp is valid (format and not is the future or to much time before)
    def __init__(self, timestamp: datetime, level:str,event_type:str, message:str):
        self.timestamp = timestamp
        self.level = level
        self.event_type = event_type
        self.message = message

    @classmethod
    def parse_line(cls, line: str) -> "LogEntry":
        timestamp_str, lvl_str, ev_type, msg = line.strip().split(" ", 3)
        ts = datetime.fromisoformat(timestamp_str)
        # no enum conversion, keep lvl_str as-is
        return cls(ts, lvl_str, ev_type, msg)

