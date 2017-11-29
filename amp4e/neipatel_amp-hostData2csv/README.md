**Summary**

This tool will query AMP for endpoint for all endpoints and export to a HOST input CSV for Firepower Management Center

**Files**
```
amp_api.py
parameters.json
amphost2csv.py
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
"group_name" : "<source group of endpoints>"

```

Example configuration file:

```
"debug" : true,
"id": "c57f21cdee54c6421795",
"api_key" : "2a0d74b2-ba1e-4698-a751-b9ef8807e3df",
"endpoint" : "api.amp.cisco.com",
"group_name" : "Protect"
```

To execute the script from the OS shell run either:

`python amphost2csv.py`
or
`./amphost2csv.py`

The script will output

`hostinputcsv.txt`

This file can be used in the FMC Host Input API.
