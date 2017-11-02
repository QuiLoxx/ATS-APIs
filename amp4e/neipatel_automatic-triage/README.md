**Summary**

This tool will take endpoints and move them from a source group to a destionation group. The movement of endpoints will be based on an event name. The idea is to automatically place endpoints into a "triage" group when a specific event is triggered

NOTE: Logging for this script will generate a `debug.log` file in the execution directory.

**Files**
```
automatic_triage.py
parameters.json
rest_methods.py
```

**Dependencies**
```
import requests
import json
```

**Usage**
Modify all fields in the `parameters.json` file to match the needs  
```

"debug" : <true/false>,
"id": "<amp4e api client id>",
"api_key" : "<amp4e api key>",
"endpoint" : "<api endpoints url>",
"group_name" : "<source group of endpoints>",
"dest_group" : "<destiation group for affected endpoints>",
"event_name" : "<amp event name to trigger move>"

```

Example configuration file:

```
"debug" : true,
"id": "c57f21cdee54c6421795",
"api_key" : "2a0d74b2-ba1e-4698-a751-b9ef8807e3df",
"endpoint" : "api.amp.cisco.com",
"group_name" : "Protect",
"dest_group" : "Triage",
"event_name" : "Threat Quarantined"
```

To execute the script from the OS shell run either:

`python automatic_triage.py`
or
`./automatic_triage.py`
