# TODO:

## Question I would like to ask:
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


## Log file format:
* MAke sure the format is valid <timeStanp>, <level>, Event_type>, <Message>.

## Configuration file
* put attention to comments '#' (maybe there is another types of comments. you should checkk)




## Additional:
* use cache for beteer performance
* maybe multi threads? maybe map_reduce?
