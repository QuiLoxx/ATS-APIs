# ANC-STEALTHWATCH-ISE
API examples for Cisco Stealthwatch

**Summary**

This tool will take endpoints associated with specific security events in Stealthwatch and automatically assign a different ANC label to them in Cisco ISE.

NOTE: Logging for this script will generate a `debug.log` file in the execution directory.

**Files**

| File Name | Purpose |
| --------- | ------- |
| rtc_stealthwatch_ise.py | main script that will retrieve all the security events and associated endpoint's IP addresses from Cisco Stealthwatch for the provided list of Security Event IDs and then auto-assign ANC labels for those endpoints in Cisco ISE |
| parameters.json | stores the hostnames & credentials |
| rest_methods.py | contains supporting functions |
| get-stealthwatch-security-event-list.py | standalone script that will retrieve all the Security Events IDs defined in Stealthwatch. This is required to be executed at least once to get the list of event ids and select the event ids that needs to be used by our RTC script for Auto-ANC |
| get-anc-labels.py | standalone script that will retrieve all the ANC labels defined in ISE |
| get-anc-endpoints.py | standalone script that will retrieve all the endpoints assigned with ANC labels from ISE |


**Dependencies**

```
import rest_methods
import json
from datetime import datetime, timedelta
import re
import time
import sys
import os.path
```

**Usage**

Modify all fields in the `parameters.json` file to match the needs  

```
"debug" : <true/false>,
"SMC_hostname" : "<Stealthwatch SMC hostname / IP>",
"SMC_username" : "<Stealthwatch SMC username>",
"SMC_password" : "<Stealthwatch SMC password>",
"SMC_tenant_id" : "123", <tenant id in Stealthwatch. If you do not know, leave it to default 123>
"ISE_hostname" : "<ISE hostname / IP>",
"ISE_port" : "9060", <ERS Port.If you do not know, leave it to default 9060 >
"ISE_username" : "<ISE username w/ ERSAdmin role",
"ISE_password" : "<ISE password"
```

Example configuration file:

```
"debug" : true,
"SMC_hostname" : "sw-smc.mango.local",
"SMC_username" : "admin",
"SMC_password" : "M1ngo@123",
"SMC_tenant_id" : "123",
"ISE_hostname" : "ise.mango.local",
"ISE_port" : "9060",
"ISE_username" : "admin",
"ISE_password" : "M1ngo@123"
```

```
Sample environment setup:
+ ISE implementation with external restful services (ERS) enabled.
+ Stealthwatch implementation
+ Windows/Unix/Linux/BSD/macOS system with Python to run these scripts
```

```
Within Stealthwatch, please configure a few custom Security Events or identify a few default Security Event IDs for which you the associated source/target/both IP addresses to be auto-contained using ISE. Once you identity that list of Security Event IDs, run the script 'get-stealthwatch-security-event-list.py'. This will pull all the Security Event IDs from Stealthwatch. Edit the 'stealthwatch_security_events-list.txt'. You need to uncomment the required Security Event IDs from this file.
  
Within ISE, there is one ANC label (ISE calls these policies) that we are concerned with:
  1. ANC-KickFromNetwork.  The label to assign an endpoint when wishing to blacklist / nuke it from orbit.

Note that this ANC label is hard-coded in the RTC script. In the future versions of this script, we will add the support to choose which ANC label for individual Security Event IDs.
```

**Script Execution**

```
To execute the script from the OS shell run:

+ 'python get-stealthwatch-security-event-list.py' # this will reach out to Stealthwatch via the REST API and retrieve all the Security Event IDs defined in Stealthwatch and write them to a 'stealthwatch_security_events-list.json' and 'stealthwatch_security_events-list.txt' file.

+ Edit the 'stealthwatch_security_events-list.txt' file in any text editor. Uncomment the Security Event IDs for which you want to run Auto-ANC. Save the file.

`rtc_stealthwatch_ise.py` # this will reach out to the Stealthwatch using the REST API and look for any Security Events with the Security Event IDs defined in the 'stealthwatch_security_events-list.txt' file withint last 1 hour. Source and Target IP addresses asociated with these events are retrieved. Then the script will also reach out to ISE via the ERS API and assign the endpoint the ANC-KickFromNetwork label, triggering a change of authorization (CoA-Reath).
```
