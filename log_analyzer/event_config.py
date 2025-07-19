import re
from dataclasses import dataclass
from log_analyzer import error_messages

# Supported configuration flags for event rules
LEVEL_FLAG = "--level"      # Filters entries by log level (e.g., "ERROR")
COUNT_FLAG = "--count"      # Reports only the number of matching entries
PATTERN_FLAG = "--pattern"  # Filters entries whose message matches a regex pattern

# Set of all allowed flags for validation
ALLOWED_FLAGS = {LEVEL_FLAG, COUNT_FLAG, PATTERN_FLAG}


@dataclass
class EventConfig:
    """
    Represents a single event rule parsed from the configuration file.

    Attributes:
        event_type (str): Name of the event to match.
        count (bool): Whether only a count of matching entries should be reported.
        level (str | None): Optional log level to match.
        pattern (re.Pattern | None): Optional compiled regex pattern to match the message.
    """
    event_type: str
    count: bool
    level: str | None
    pattern: re.Pattern | None


def load_configs(path: str) -> list[EventConfig]:
    """
    Parses a configuration file and returns a list of EventConfig objects.

    Each non-empty, non-comment line must start with an event type,
    optionally followed by  flags: [--count, --level LEVEL, --pattern REGEX]

    Args:
        path (str): Path to the events configuration file.

    Returns:
        list[EventConfig]: A list of parsed event configuration objects.
    """
    configs: list[EventConfig] = []
    with open(path, 'r', encoding='utf-8') as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            config = _parse_event_line(line)
            configs.append(config)

    return configs


def _parse_event_line(line: str) -> EventConfig:
    """ Parses a single configuration line into an EventConfig object."""
    tokens = line.split()
    event_type = tokens[0]
    flags = _parse_flags(tokens[1:], line)

    count = flags.get(COUNT_FLAG, False)
    level = flags.get(LEVEL_FLAG)
    pattern_str = flags.get(PATTERN_FLAG)
    pattern = re.compile(pattern_str) if pattern_str else None

    return EventConfig(event_type=event_type, count=count, level=level, pattern=pattern)


def _parse_flags(tokens: list[str], original_line: str) -> dict:
    """
    Extracts flags and their values from a tokenized config line.
    """
    flags = {}
    idx = 0
    while idx < len(tokens):
        flag = tokens[idx]

        if flag == COUNT_FLAG:
            flags[COUNT_FLAG] = True
            idx += 1

        elif flag in {LEVEL_FLAG, PATTERN_FLAG}:
            if idx + 1 >= len(tokens):
                raise ValueError(error_messages.MISSING_VALUE_ERR.format(flag=flag, line=original_line))

            idx += 1
            value_parts = []
            while idx < len(tokens) and tokens[idx] not in ALLOWED_FLAGS:
                value_parts.append(tokens[idx])
                idx += 1
            raw = " ".join(value_parts)

            if (raw.startswith('"') and raw.endswith('"')) or(raw.startswith("'") and raw.endswith("'")):
                raw = raw[1:-1]

            flags[flag] = raw

        else:
            allowed = ", ".join(sorted(ALLOWED_FLAGS))
            raise ValueError(error_messages.INVALID_FLAG.format(flag=flag, line=original_line, allowed=allowed))

    return flags

