**Summary**

This tool uses both python and perl to establish communications with Security Center and FMC to add vulnerability scan data (from Security Center) to the Host profile in FMC. For more detailed instructions please use the "Readme.pdf"

**Files**

`query_vuln.py`


**Dependencies**
```
import requests
import json
import subprocess
import pysecuritycenter
```

**Usage**

The script is fed by one user configurable file: “parameters.json.” These are the variables used to define the details of the Security Center and FMC that will be used
```
{
"hostname" : "<hostname or ip of security center>",
"FMCHostname" : "<hostname or ip of FMC>",
"username" : "<Security Center Username>",
"password" : "<Security Center Password>",
"debug" : true,
"netrange" : "<IP Range of hosts to add>",
"addHosts" : true
}

It is recommended to leave the debug parameter true to help with troubleshooting if you were to have issues.

The addHosts parameter should only be set to “false” if you know for certain that the hosts for which you are adding vulnerability details already exist in the FMC.

```

Before running the following command ensure that all prerequisites are met and the *.pcks12 file from the FMC is in the same directory.
To run the tool simply execute:

`python query_vuln.py`

or

`./query_vuln.py`
