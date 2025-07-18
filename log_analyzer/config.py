# TODO - documentation
import re
import shlex
from dataclasses import dataclass
from typing import List, Optional, Pattern
from log_analyzer import error_messages

LEVEL_FLAG = "--level"
COUNT_FLAG = "--count"
PATTERN_FLAG = "--pattern"
ALLOWED_FLAGS = {LEVEL_FLAG, COUNT_FLAG, PATTERN_FLAG}


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

            tokens = shlex.split(line)  # shlex.split handles quoted regex patterns correctly
            event_type = tokens[0]  # First token is the event_type

            # Defaults
            count = False
            level = None
            pattern = None

            # Parse flags
            idx = 1
            while idx < len(tokens):
                flag = tokens[idx]

                if flag == COUNT_FLAG:
                    count = True
                    idx += 1

                elif flag == LEVEL_FLAG:
                    if idx + 1 >= len(tokens):
                        raise ValueError(error_messages.MISSING_VALUE_ERR.format(flat=flag, line=line))
                    level = tokens[idx+1]
                    idx += 2

                elif flag == PATTERN_FLAG:
                    if idx + 1 >= len(tokens):
                        raise ValueError(error_messages.MISSING_VALUE_ERR.format(flat=flag, line=line))
                    pattern = re.compile(tokens[idx+1]) # compile the regex
                    idx += 2

                else:
                    allowed = ", ".join(sorted(ALLOWED_FLAGS))
                    raise ValueError(
                        error_messages.INVALID_FLAG.format(flag=flag, line=line, allowed=allowed)
                    )

            configs.append(EventConfig(
                event_type=event_type,
                count=count,
                level=level,
                pattern=pattern
            ))

    return configs
