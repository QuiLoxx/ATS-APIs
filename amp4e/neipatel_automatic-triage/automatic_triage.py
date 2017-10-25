import rest_methods
import json

##Import variables to get configuration
config = json.loads(open("parameters.json").read())
log = open ("debug.log","w")
##Set Variables for use
debug = config["debug"]
client_id = config["id"]
api_key = config["api_key"]
endpoint = config["endpoint"]
group_name = config["group_name"]
event_name = config["event_name"]
dest_group = config["dest_group"]

##get the event id that we are looking for
url = "https://{}:{}@{}/v1/event_types".format(client_id,api_key,endpoint)
if debug:
	log.write("** DEBUG: URL for request is :{}\n".format(url))
response = rest_methods.get(url)
for event in response["data"]:
	if event["name"] == event_name:
		event_id = event["id"]
		if debug:
			log.write("** DEBUG: Found Event Type!\n")
if debug:
	log.write("** DEBUG: Event id is:{}\n".format(event_id))

##get group GUID for the group we want
url = "https://{}:{}@{}/v1/groups".format(client_id,api_key,endpoint)
if debug:
	log.write("** DEBUG: URL for request is :{}\n".format(url))
response = rest_methods.get(url)

for group in response["data"]:
	if group["name"] == group_name:
		group_id = group["guid"]
		if debug:
			log.write("** DEBUG: Found source Group Name id - {} \n".format(group_id))
	elif group["name"] == dest_group:
		dest_group_id = group["guid"]
		if debug:
			log.write("** DEBUG: Found dest Group Name id - {} \n".format(dest_group_id))


##Get all events for defined group and type
url = "https://{}:{}@{}/v1/events?group_guid[]={}&event_type[]={}".format(client_id,api_key,endpoint,group_id,event_id)
if debug:
	log.write("** DEBUG: URL for request is :{}\n".format(url))
response = rest_methods.get(url)
affected_computers = []
for events in response["data"]:
	affected_computers.append(events["computer"]["connector_guid"])
	if debug:
		log.write ("** DEBUG: Affected computer found based on event {}\n".format(events["computer"]["connector_guid"]))
##prune list for only unique values
unique_list = set(affected_computers)
if debug:
	for val in unique_list:
		log.write("** DEBUG: Affected Computer id: {}\n".format(val))

##Now that we have a list of the affected computers time for you to move them into a new group

body = {"group_guid": dest_group_id}
for computer in unique_list:
	url = "https://{}:{}@{}/v1/computers/{}".format(client_id,api_key,endpoint,computer)
	response = rest_methods.patch(url, body)
	if debug:
		log.write("** DEBUG: Affected Computer id: {} move to new group\n".format(computer))


print "DONE ! - Thank you for particpating in the AMP API Workshop"
log.close()
