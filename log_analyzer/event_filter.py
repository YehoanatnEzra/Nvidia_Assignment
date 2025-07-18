import re
from config import EventConfig
from log_entry import LogEntry


class EventFilter:
    """
    Wraps one EventConfig and exposes a matches(entry) -> bool method.
    """
    def __init__(self, cfg: EventConfig):
        self.event_type: str = cfg.event_type
        self.count:      bool = cfg.count
        self.level:      str | None = cfg.level
        self.pattern:    re.Pattern | None = cfg.pattern

    def matches(self, entry: LogEntry) -> bool:
        # event_type must match exactly
        if entry.event_type != self.event_type:
            return False

        # if a level was specified, it must match
        if self.level is not None and entry.level != self.level:
            return False

        # if a regex pattern was specified, it must be found in the message
        if self.pattern is not None and not self.pattern.search(entry.message):
            return False

        return True
