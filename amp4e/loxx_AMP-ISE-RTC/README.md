# ANC-AMP-ISE
API examples for Cisco Advanced Threat Solutions

**Summary**

This tool will take endpoints and move them from a source group to a destination group. The movement of endpoints will be based on an event name. The idea is to automatically place endpoints into a "triage" group when a specific event is triggered

NOTE: Logging for this script will generate a `debug.log` file in the execution directory.

**Files**
```
rtc_amp_ise.py
parameters.json
rest_methods.py
anc_endpoints.json
anc_lables.json
get-anc-endpoints.py
get-anc-labels.py
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
"event_name" : "<amp event name to trigger move>",
"host" : "<ISE fqdn>",
"port" : "<ERS Port>",
"username" : "<ise username w/ ERSAdmin role",
"password" : "<password>"

```

Example configuration file:

```
"debug" : true,
"id": "c57f21cde3d3c6421795",
"api_key" : "2a0d74b2-ba1e-4104-a751-b9ef8807e3df",
"endpoint" : "api.amp.cisco.com",
"group_name" : "Protect",
"dest_group" : "Triage",
"event_name" : "Threat Quarantined"
"host" : "ise.woland.com",
"port" : "9060",
"username" : "roger_rabbit",
"password" : "JessicaR0cks"
```

```
Sample environment setup:
+ ISE implementation with external restful services (ERS) enabled.
+ AMP for Endpoints public cloud
+ Unix/Linux/BSD/macOS system with Python to run these scripts
```

```
Within AMP, there are 3 sample groups that we are concerned with:
  1. ATW-Production.  All the demo endpoints are members of this group to start with.
  2. ATW-Triage.  A group to assign endpoints to when they are being investigated further.
  3. ATW-Isolate.  A group to assign endpoints to when they are positively identified as malicious, and will be kicked off the network.  
  
Within ISE, there are two ANC labels (ISE calls these policies) that we are concerned with:
  1. ANC-Investigate.  The label to assign an endpoint when wishing to investigate it further.
  2. ANC-KickFromNetwork.  The label to assign an endpoint when wishing to blacklist / nuke it from orbit.
  
```

**Script Execution**
```
To execute the script from the OS shell run:

+ 'python get-anc-labels.py' # this will reach out to ISE via the ERS API and retrieve all the configured ANC labels (aka:ANC policies) and write that data to the anc_lables.json file.

+ 'python get-anc-endpoints' # this will reach out to ISE via the ERS API and retrieve all the endpoints that have an ANC classification and write that data to the anc_endpoints.json file.

`python rtc_amp_ise.py` # this will reach out to the AMP public cloud using the REST API and look for any endpoints within the configured source group that have an event name matching one of two strings:
  1.  "Threat Quarantined".  Endpoints within the defined group with events matching this name will be moved into the ATW-Isolate group and then the script will also reach out to ISE via the ERS API and assign the endpoint the ANC-KickFromNetwork label, triggering a change of authorization (CoA-Reath).
  2.  "Threat Detected".  Endpoints within the defined group with events matching this name will be moved into the ATW-Triage group and then the script will also reach out to ISE via the ERS API and assign the endpoint the ANC-Investigate label, triggering a change of authorization (CoA-Reath).
  
After the computers are identitified, they are assigned ANC Labels & then moved into a new group in AMP.
ANC-KickFromNetwork
ANC-Investigate
```
