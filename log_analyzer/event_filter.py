import re
from log_analyzer.event_config import EventConfig
from log_analyzer.log_entry import LogEntry


class EventFilter:
    """
    Filters log entries based on a given EventConfig.

    Checks:
    - entry.event_type must match config.event_type
    - If config.level is set, entry.level must match
    - If config.pattern is set, entry.message must match the regex
    """
    def __init__(self, ev_config: EventConfig):
        """
        Initializes the filter with a specific event configuration.
        """
        self.event_type: str = ev_config.event_type
        self.count:      bool = ev_config.count
        self.level:      str | None = ev_config.level
        self.pattern:    re.Pattern | None = ev_config.pattern

    def matches(self, entry: LogEntry) -> bool:
        """
           Determine if a given log entry matches the filter conditions.

           A match occurs if:
           - The event_type matches exactly.
           - If a level is specified, it must match the entry's level.
           - If a pattern is specified, it must match the entry's message.

           Returns:
               bool: True if the entry matches all applicable conditions, False otherwise.
           """
        return (
                entry.event_type == self.event_type and
                (self.level is None or entry.level == self.level) and
                (self.pattern is None or bool(self.pattern.search(entry.message)))
        )



