**Summary**

This tool will take create a large number of access control rules (# is configurable) in an FMC with random details inside as an example on how to build rules. This can also be used to test performace of FMC with a large ACP.

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
Modify the `user config variable section` in the `setup.py` file to match the needs  
```
fmc_hostname = "<FMC hostname/IP>"
fmc_username = "<FMC Username>"
fmc_password = "<FMC Password>"
domain = "<FMC Domain>"
number_of_rules = #of rules to add
```

Example configuration:

```
fmc_hostname = "FMC4k.example.local"
fmc_username = "api-script"
fmc_password = "myPassword"
domain = "Global"
number_of_rules = 200
```

To execute the script from the OS shell run either:

`python setup.py`
or
`./setup.py`

This tool also has a cleanup functionality where all created rules will be deleted. To run cleanup at the prompt:

`Would you like to cleanup? [1/0]`

enter `1` to remove rules or `0` to keep them.
