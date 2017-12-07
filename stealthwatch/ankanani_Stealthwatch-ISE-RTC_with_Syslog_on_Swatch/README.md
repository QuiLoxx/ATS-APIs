# ANC-STEALTHWATCH-ISE
API examples for Cisco Stealthwatch

**Summary**

This tool will take endpoints associated with specific security events in Stealthwatch and automatically assign a different ANC label to them in Cisco ISE.

NOTE: Logging for this script will generate a `swalerts_logfile.log` and `alarms_addressed_by_anc.log` files in the execution directory.

**Files**

| File Name | Purpose |
| --------- | ------- |
| sw-rtc.py | main script that will listen to all the security event syslogs from SMC, finds out specified security alarms and associated endpoint's IP addresses; then auto-assign ANC labels for those endpoints in Cisco ISE |
| parameters.json | stores the hostnames & credentials |
| rest_methods.py | contains supporting functions |
| get-anc-labels.py | standalone script that will retrieve all the ANC labels defined in ISE |
| get-anc-endpoints.py | standalone script that will retrieve all the endpoints assigned with ANC labels from ISE |


**Dependencies**

```
import logging
import SocketServer
import threading
import re
import jsonpickle
import pprint
import time
import sys
import json
import requests
import os
import rest_methods
from datetime import datetime, timedelta
```

**Usage**

Modify all fields in the `parameters.json` file to match the needs  

```
LIST_OF_STEALTHWATCH_ALARMS_TO_BE_CONSIDERED_FOR_ISE_AUTO_REMEDIATION = ['','']     # Comma separated list of stealthwatch security event names like shown here that you want to use for auto ANC
ISE_HOSTNAME = 'ise.mango.local'
ISE_ADMIN_USERNAME = '<ISE username with minimum ANC/admin privileges>'
ISE_ADMIN_PASSWORD = '<ISE password>'
```

Example configuration file:

```
LIST_OF_STEALTHWATCH_ALARMS_TO_BE_CONSIDERED_FOR_ISE_AUTO_REMEDIATION = ['Bad Host','CSE: Employees to BlackHole High Traffic']
ISE_HOSTNAME = 'ise.mango.local'
ISE_ADMIN_USERNAME = 'admin'
ISE_ADMIN_PASSWORD = 'M1ngo@123'
```

```
Sample environment setup:
+ ISE implementation with external restful services (ERS) enabled.
+ Stealthwatch implementation
+ Windows/Unix/Linux/BSD/macOS system with Python to run these scripts
```

```
Within Stealthwatch, please configure it to send syslogs for security events to the server where you are running this script.
To configure this in smc. open the java swing client of smc. navigate to configuration -> response management -> rules. add a name and select enable. select the rule as - all severity informational or higher.
move to action. click on add -> add -> provide ip address of the host where you are going to run this script. click on syslog formats -> add -> put the below template, give it a name and save it.save everything and close.

Lancope|StealthWatch|Notification:{alarm_type_id}|{alarm_type_name}|{alarm_severity_id}| alarm_desc="{alarm_type_description}" details="{details}" dst={target_ip}  src={source_ip}  start={start_active_time}  end={end_active_time}  cat={alarm_type_name} Alarm_ID={alarm_id} Source_HG={source_host_group_names} Target_HG={target_host_group_names} Source_HostSnapshot={source_url} Target_HostSnapshot={target_url} dpt={port} proto={protocol} FC_Name={device_name} FC_IP={device_ip} Domain={domain_id} tcn={target_country_name} scn={source_country_name} alarmsev={alarm_severity_name} alarmstatus={alarm_status}

  
Within ISE, there is one ANC label (ISE calls these policies) that we are concerned with:
  1. ANC-KickFromNetwork.  The label to assign an endpoint when wishing to blacklist / nuke it from orbit.

Note that this ANC label is hard-coded in the RTC script. In the future versions of this script, we will add the support to choose which ANC label for individual Security Event IDs.
```

**Script Execution**

```
To execute the script from the OS shell run:

+ 'python sw-rtc.py' # this will start a multi-threaded server. One thread will listen to syslogs from SMC and append them to a 'swalerts_logfile.log' file. Another thread will tail the 'swalerts_logfile.log' file for any new syslogs.
Any new syslogs will be parsed and the security event names will be compared with the ones that are there in the provided list.
Hence before running this script, ensure that you have added the security event names for which you want auto ANC.
The source IP address will be retrieved from these specific security events Then the script will also reach out to ISE via the ERS API and assign the endpoint the ANC-KickFromNetwork label, triggering a change of authorization (CoA-Reath).
The alarms that are addressed with auto ANC are added to 'alarms_addressed_by_anc.log' file.
```
