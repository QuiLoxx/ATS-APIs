**Summary**

This tool starts an AMQP event stream using the AMP4e API and prints event data live to a screen

**Files**
```
parameters.json
amp_api.py
amp_event_stream.py
```
**Dependencies**
```
import requests
import json
import pika
```

**Usage**
Enter the api credentials for your amp for endpoints account and the group for which you would like to start a stream in the `parameters.json` file

```
{
	"debug" : true,
	"client_id": "",
	"api_key" : "",
	"endpoint" : "",
	"group_name" : "",
	"event_type" : ""
}

```


An example of the `parameters.json` file is below

```
{
	"debug" : true,
	"client_id": "2cee1c2200a2e9d63f53",
	"api_key" : "bef01fff-7b9b-4f4b-887b-1db821f07ceb",
	"endpoint" : "api.amp.cisco.com",
	"group_name" : "",
	"event_type" : ""
}

```

To execute the script from the OS shell run either:

`./amp_event_stream.py`
or
`python amp_event_stream.py`
