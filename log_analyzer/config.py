# TODO - documentation
import re
import shlex
from dataclasses import dataclass
from typing import List, Optional, Pattern

@dataclass
class EventConfig:
    """
    Represents one rule from the events file.
    """
    event_type: str              # e.g. "UserLogin"
    count:      bool              # True if we should only tally matches
    level:      Optional[str]     # e.g. "ERROR", or None to match any level
    pattern:    Optional[Pattern] # compiled regex to apply to the message, or None


def load_configs(path: str) -> List[EventConfig]:
    """
    Load rules from a file such as 'events_sample.txt'.
    Each line is:
        EVENT_TYPE [--count] [--level LEVEL] [--pattern REGEX]
    Blank lines and lines starting with '#' are ignored.
    """
    configs: List[EventConfig] = []

    with open(path, 'r', encoding='utf-8') as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith('#'):
                continue

            # shlex.split handles quoted regex patterns correctly
            tokens = shlex.split(line)
            # First token is the event_type
            event_type = tokens[0]

            # Defaults
            count   = False
            level   = None
            pattern = None

            # Parse flags
            idx = 1
            while idx < len(tokens):
                flag = tokens[idx]
                if flag == '--count':
                    count = True
                    idx += 1
                elif flag == '--level':
                    if idx + 1 >= len(tokens):
                        raise ValueError(f"Missing value for --level in line: {line!r}")
                    level = tokens[idx+1]
                    idx += 2
                elif flag == '--pattern':
                    if idx + 1 >= len(tokens):
                        raise ValueError(f"Missing value for --pattern in line: {line!r}")
                    # compile the regex
                    pattern = re.compile(tokens[idx+1])
                    idx += 2
                else:
                    raise ValueError(f"Unknown flag '{flag}' in config file: {line!r}")


            configs.append(EventConfig(
                event_type=event_type,
                count=count,
                level=level,
                pattern=pattern
            ))

    return configs
