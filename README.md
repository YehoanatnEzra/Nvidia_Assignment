TODO:

## Question I would like to ask:
* should process only files that end with .log or .log.gz, and ignore all other file type
* <level> and <event_type> must to be with upcase letter?
* <if no, same level\event level but one with upcase letter and the other with down letter - its considered as a differents levels/event levels or is the same?
* There’s a strict rule on level or event level

### input:
* Should decide what to do if the folder path or the event_file path is invalid
*  Check if the time stamp is valid (12 months, and number of the days are correclt. maybe I should check how many days exist each month)
* Check if "from "timestamp" is indeed before "to timestamp"
* check if "from timestamp" and "from timestamp" is indeed a valid and reasonable time (not somthing in the future or before 100 year (constant invalid year)


### Log file format:
* Make sure the format is valid <timeStanp>, <level>, Event_type>, <Message>.

### Configuration file
* put attention to comments '#' (maybe there is another types of comments. you should checkk)

### CLI UX:
* Flags - h, --help-
  

## Additional:
* use cache for better performance
* maybe multi threads? maybe map_reduce?
  

