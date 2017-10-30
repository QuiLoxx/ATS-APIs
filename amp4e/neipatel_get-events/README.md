**Summary**

This tool prints out all event types in AMP for Endpoints to the screen with their corresponding IDs. Based on selected event ID it will also print all events of specified type to screen

**Files**

`events.py`

**Dependencies**
```
import requests
import json
```

**Usage**
Enter the api credentials for your amp for endpoints account and the event ID you are interested in (found between lines 20 and 23)  
```
client_id = ""
api_key = ""
event_id = ""
```

To execute the script from the OS shell run either:

`python events.py`
or
`./events.py`
