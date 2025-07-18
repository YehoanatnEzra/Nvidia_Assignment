| Python File                   | Description                                                                                                                  |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **main.py**                   | CLI entry point: parses command-line arguments (log dir, events file, optional time filters) and invokes the `LogAnalyzer`.  |
| **log\_analyzer/entry.py**    | Defines `LogEntry`: data model for a single log line (timestamp, level, event type, message) and the `parse_line()` factory. |
| **log\_analyzer/config.py**   | Defines `EventConfig` (dataclass for one rule) and `load_configs()` to read & parse the events file.                         |
| **log\_analyzer/filter.py**   | Defines `EventFilter`: wraps an `EventConfig` and exposes `matches(LogEntry)` to test entries.                               |
| **log\_analyzer/analyzer.py** | Implements `LogAnalyzer`: loads configs, gathers & filters `LogEntry` objects, and reports counts or matching lines.         |
| **log\_analyzer/cache.py**    | Implements `CacheEngine`: simple wrapper around `functools.lru_cache` (and pluggable backends) for caching expensive calls.  |
| **tests/test\_entry.py**      | Unit tests for `LogEntry.parse_line()` and its error handling.                                                               |
| **tests/test\_config.py**     | Unit tests for `load_configs()` and validation of `EventConfig` parsing.                                                     |
| **tests/test\_filter.py**     | Unit tests for `EventFilter.matches()` under various rule combinations.                                                      |
| **tests/test\_analyzer.py**   | End-to-end tests for `LogAnalyzer.run()`, including CLI args, time filtering, and output formatting.                         |
| **tests/test\_cache.py**      | Unit tests for `CacheEngine.cache()` behavior and cache invalidation.                                                        |


## Question I would like to ask:
* should process only files that end with .log or .log.gz, and ignore all other file type
* <level> and <event_type> must to be with upcase letter?
* <if no, same level\event level but one with upcase letter and the other with down letter - its considered as a differents levels/event levels or is the same?

## Testing in my program:
### genearal:
* Maybe I should implement a test function that make sure the time is correctly. (maybe outside function).

### input:
* Should decide what to do if the folder path or the event_file path is invalid
*  Check if the time stamp is valid (12 months, and number of the days are correclt. maybe I should check how many days exist each month)
* Check if "from "timestamp" is indeed before "to timestamp"
* check if "from timestamp" and "from timestamp" is indeed a valid and reasonable time (not somthing in the future or before 100 year (constant invalid year)


### Log file format:
* MAke sure the format is valid <timeStanp>, <level>, Event_type>, <Message>.

### Configuration file
* put attention to comments '#' (maybe there is another types of comments. you should checkk)

### CLI UX:
* Flags - h, --help-
  - 
* Usage: tiny description of the subcommends and the flags
* Sucommands:
* - -...
  


## Additional:
* use cache for beteer performance
* maybe multi threads? maybe map_reduce?
  

## questions:
- There’s a strict rule on level or event level?
