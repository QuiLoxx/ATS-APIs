**Summary**
This tool will create a policy with one rule and monitor the time of day, based on the time of day the rule will either be enabled or disabled


**Files**
```
connect.py
setup.py
```

**Dependencies**
```
import requests
import json
import datetime
import time
```

**Usage**
Modify the `user config variable section` in the `setup.py` file to match the needs  
```
fmc_hostname = "<FMC hostname/IP>"
fmc_username = "<FMC Username>"
fmc_password = "<FMC Password>"
domain = "<FMC Domain>"
off_time_range = "<time range for rule to be off in 24-hr format>"
```

Example configuration:

```
fmc_hostname = "FMC4k.example.local"
fmc_username = "api-script"
fmc_password = "myPassword"
domain = "Global"
off_time_range = "16:00-08:00"
```

To execute the script from the OS shell run either:

`python setup.py`
or
`./setup.py`

To terminate the process press "CNTRl-C"
