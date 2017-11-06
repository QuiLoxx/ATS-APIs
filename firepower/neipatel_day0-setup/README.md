**Summary**

This tool will setup some initial objects policies and rules in FMC for example of Day 0 Orchestration

**Files**
```
connect.py
setup.py
```

**Dependencies**
```
import requests
import json
import sys
```

**Usage**
Modify the `user config variable section` in the `setup.py` file to match the needs  (lines 5 - 11)
```
fmc_hostname = ""
fmc_username = ""
fmc_password = ""
device_name = ""
device_hostname = ""
regkey = ""
domain = ""
```

Example configuration:

```
fmc_hostname = "FMC4k.example.local"
fmc_username = "api-script"
fmc_password = "myPassword"
device_name = "ngfw"
device_hostname = "ngfw.example.local"
regkey = "passkey"
domain = "Global/test/test-nested"
```

To execute the script from the OS shell run either:

`python setup.py`
or
`./setup.py`

This tool also has a cleanup functionality where all created rules will be deleted. To run cleanup at the prompt:

`Would you like to cleanup? [1/0]`

enter `1` to remove rules or `0` to keep them.
