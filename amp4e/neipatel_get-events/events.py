import requests
import json

#function definitions
def get(url):
	try:
	    response = requests.get(url)
	    # Consider any status other than 2xx an error
	    if not response.status_code // 100 == 2:
	        return "Error: Unexpected response {}".format(response)
	    try:
	        return response.json()
	    except:
	        return "Error: Non JSON response {}".format(response.text)
	except requests.exceptions.RequestException as e:
	    # A serious problem happened, like an SSLError or InvalidURL
	    return "Error: {}".format(e)

#main code ENTER YOU CLIENT ID AND API KEY HERE
client_id = ""
api_key = ""
#Enter the event type you would like to return here
event_id = ""

event_id_url = "https://{}:{}@api.amp.cisco.com/v1/event_types".format(client_id,api_key)

event_ids= get(event_id_url)
event_types = {}
for e_id in event_ids["data"]:
    event_types[e_id["name"]] = e_id["id"]


for key,value in event_types.iteritems():
    print "{}:{}".format(value,key)

#get event data for executed malware (use the above output for reference)
event_url  = "https://{}:{}@api.amp.cisco.com/v1/events?event_type[]={}".format(client_id,api_key,event_id)
events = get(event_url)

#parse through event data and get only relevant information

for data in events["data"]:
    print data
