**Summary**

This tool uses both python and perl to establish communications with Security Center and FMC to add vulnerability scan data (from Security Center) to the Host profile in FMC.

**Files**

`import_vuln.py`


**Dependencies**
```
import security_center as sc (included in this package)
import threading
import subprocess
import time
import ConfigParser
```

**Usage**

The script is fed by one user configurable file: “config.cfg” These are the variables used to define the details of the Security Center and FMC that will be used
```
[UserVariables]
username = <security center username>
password = <security center password>
address = <security center IP/Hostname>
debug = True
ip_range = 10.0.0.0/8
page_size = 100
fmc = 192.168.207.135
delay = <time in seconds between update runs>
quiet = <True or False, defines if command output is noisy or quiet>

EXAMPLE CONFIG FILE
[UserVariables]
username = administrator-api
password = thisisthepassword
address = securitycenter.acme.com
debug = False
ip_range = 192.168.1.0/24
page_size = 100
fmc = fmc.acme.com
delay = 1200
quiet = True

It is recommended to leave the debug parameter true to help with troubleshooting if you were to have issues.
```

Before running the following command ensure that all prerequisites are met and the *.pcks12 file from the FMC is in the same directory.
To run the tool simply execute:

`python import_vuln.py`

or

`./import_vuln.py`
