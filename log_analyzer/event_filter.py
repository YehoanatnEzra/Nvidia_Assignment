import re
from log_analyzer.event_config import EventConfig
from log_analyzer.log_entry import LogEntry


class EventFilter:
    """
       Wraps one EventConfig and check if Check that entry.event_type matches the config.event_type.
       If config.level is set or config.pattern is set,  verify is matches entry.level/pattern equals it.
       """
    def __init__(self, ev_config: EventConfig):
        self.event_type: str = ev_config.event_type
        self.count:      bool = ev_config.count
        self.level:      str | None = ev_config.level
        self.pattern:    re.Pattern | None = ev_config.pattern

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
