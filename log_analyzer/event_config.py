import re
from dataclasses import dataclass
from log_analyzer import error_messages

LEVEL_FLAG = "--level"
COUNT_FLAG = "--count"
PATTERN_FLAG = "--pattern"
ALLOWED_FLAGS = {LEVEL_FLAG, COUNT_FLAG, PATTERN_FLAG}


@dataclass
class EventConfig:
    event_type: str
    count: bool
    level: str | None
    pattern: re.Pattern | None


def load_configs(path: str) -> list[EventConfig]:
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
    tokens = line.split()
    event_type = tokens[0]
    flags = _parse_flags(tokens[1:], line)

    count = flags.get(COUNT_FLAG, False)
    level = flags.get(LEVEL_FLAG)
    pattern_str = flags.get(PATTERN_FLAG)
    pattern = re.compile(pattern_str) if pattern_str else None

    return EventConfig(event_type=event_type, count=count, level=level, pattern=pattern)


def _parse_flags(tokens: list[str], original_line: str) -> dict:
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
            flags[flag] = " ".join(value_parts)

        else:
            allowed = ", ".join(sorted(ALLOWED_FLAGS))
            raise ValueError(error_messages.INVALID_FLAG.format(flag=flag, line=original_line, allowed=allowed))

    return flags
