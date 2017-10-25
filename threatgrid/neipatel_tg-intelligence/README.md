**Summary**

This tool writes out two data files for use from intelligence data in Threat Grid. The two files will have shas and domains that can be used for any purporse, intelligence or enforcement. 

**Files**

`tg-intelligence-feeds.py`

**Dependencies**
```
import requests
import json
import sys
import datetime
```

**Usage**
Enter the api credentials for your Threat Grid account (found on line 34)  
```
#---------ENTER YOUR API KEY --------------#
api_key = "<your api key here>"
```

To execute the script from the OS shell run either:

`python tg-intelligence-feeds.py`
or
`./tg-intelligence-feeds.py`

The script will prompt for selection of feed you are interested in:
`What feed would you like to get? (1-11)`

The script will then return two files:

`<feed_name>_domains.txt`
`<feed_name>_shas.txt`
