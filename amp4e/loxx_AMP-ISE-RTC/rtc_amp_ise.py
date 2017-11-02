import rest_methods
import json

##  NOTES TO AARON & NEIL  ##
### 11/1/17 - Setup script to handle pagination from AMP  
### 11/1/17 - Modify scripts to use the stream API for events in AMP

# *******  SETUP SECTION  ***********
##Import variables to get configuration
config = json.loads(open("parameters.json").read())
log = open ("debug.log","w")
##Set Variables for use
debug = config["debug"]
client_id = config["id"]
api_key = config["api_key"]
endpoint = config["endpoint"]
#source group where "normal" computers are
group_name = config["group_name"]
#the event name within AMP, i.e.: Threat Detected, or Threat Quarantined
event_name = config["event_name"]
#the group to move endpoints to when a Threat Quarantined event (event_name) is seen.
dest_group = config["dest_group"]
#the event name and destination group name within AMP, for traiging, instead of Isolating. 
triage_event_name = config["triage_event_name"]
triage_dest_group = config["triage_dest_group"]
username = config["username"]
password = config["password"]
host = config["host"]
port = config["port"]
headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
        }
#atw - not using this because we hard-coded values. 
#anc_labels = json.loads(open("anc_labels.json").read())


##  *******  GET EVENT ID'S FROM AMP  *******
##get the event id that we are looking for based on the event names "Threat Quarantined"
url = "https://{}:{}@{}/v1/event_types".format(client_id,api_key,endpoint)
if debug:
	log.write("** DEBUG: URL for request is :{}\n".format(url))
# print url
response = rest_methods.ampget(url)
for event in response["data"]:
	if event["name"] == event_name:
		event_id = event["id"]
		if debug:
			log.write("** DEBUG: Found Event Type!\n")
	elif event["name"] == triage_event_name:
		triage_event_id = event["id"]
		if debug:
			log.write("** DEBUG: Found Triage Event Type!\n")
if debug:
	log.write("** DEBUG: Event id is:{}\n".format(event_id))
	log.write("** DEBUG: Event id is:{}\n".format(triage_event_id))

##  *******  GET GROUP GUIDs FROM AMP  *******
##get group GUID for the group we want, using the string name of the group
###  There are 3 groups we care about in this script.
####  Source Group = the group that we will examine for events in AMP
####  Destintation Group = the group we will move endpoints into when they have Threat Qurantined Events 
####  Triage Destintation Group = the group we will move endpoints into when they have Threat Detected Events 

url = "https://{}:{}@{}/v1/groups".format(client_id,api_key,endpoint)
if debug:
	log.write("** DEBUG: URL for request is :{}\n".format(url))
response = rest_methods.ampget(url)

for group in response["data"]:
	if group["name"] == group_name:
		group_id = group["guid"]
		if debug:
			log.write("** DEBUG: Found source Group Name id - {} \n".format(group_id))
	elif group["name"] == dest_group:
		dest_group_id = group["guid"]
		if debug:
			log.write("** DEBUG: Found dest Group Name id - {} \n".format(dest_group_id))
	elif group["name"] == triage_dest_group:
		triage_dest_group_id = group["guid"]
		if debug:
			log.write("** DEBUG: Found Triage dest Group Name id - {} \n".format(triage_dest_group_id))


##  Get all "Threat Quarantined" events for defined group and type.  
###  Quarantine means something beyond a detection has occured and will put the endpoint into the Isolated Group.
url = "https://{}:{}@{}/v1/events?group_guid[]={}&event_type[]={}".format(client_id,api_key,endpoint,group_id,event_id)
if debug:
	log.write("** DEBUG: URL for request is :{}\n".format(url))
response = rest_methods.ampget(url)
# print response

###  ****  GET THE COMPUTER OBJECTS THAT SHOWED THREAT QUARANTINED  *****
affected_computers = []
for events in response["data"]:
	affected_computers.append(events["computer"]["connector_guid"])
	# print affected_computers
	if debug:
		log.write ("** DEBUG: Affected Isolate computer found based on event {}\n".format(events["computer"]["connector_guid"]))
##prune list for only unique values
unique_list = set(affected_computers)
if debug:
	for val in unique_list:
		log.write("** DEBUG: Isolate Affected Computer id: {}\n".format(val))

###  ****  GET THE MAC ADDRESSES OF ALL INTERFACES OF EACH COMPUTER  *****
#Get the mac addresses of each computer in the unique_list.
for isolated_computer in unique_list:
	url = "https://{}:{}@{}/v1/computers/{}".format(client_id,api_key,endpoint,isolated_computer)
	response = rest_methods.ampget(url)
	#because computers may have more than one interface, network_addresses is an array.  This next for loop is to pull the mac address for each interface. 
	mac_addr = []
	for interface in response["data"]["network_addresses"]:
		mac_addr.append(interface["mac"])
		#print interface["mac"]
		log.write("** DEBUG: Isolate Affected Computer mac_addr: {}\n".format(interface["mac"]))

###  ****  ASSIGN THE ANC LABEL TO COMPUTERS THAT SHOWED "THREAT QUARANTINED"  *****
	#Trigger the ANC label assignment for Isolated Computers.  This is hard-coded for ANC-KickFromNetwork label in ISE. 
	for mac in mac_addr:
		body = {
		"OperationAdditionalData": {
		"additionalData": [{
		"name": "macAddress",
		"value": mac
		},
		{
		"name": "policyName",
		"value": "ANC-KickFromNetwork"
		}]
		}
		}
		url = "https://{}:{}@{}:{}/ers/config/ancendpoint/apply".format(username,password,host,port)
		response = rest_methods.put(url,headers,body)


###  ****  MOVE COMPUTERS THAT SHOWED "THREAT QUARANTINED" TO A NEW GROUP IN AMP  *****
##Now that we have a list of the affected computers time for you to move them into a new group
#Commenting this out to test the query before moving devices.  

body = {"group_guid": dest_group_id}
for computer in unique_list:
	url = "https://{}:{}@{}/v1/computers/{}".format(client_id,api_key,endpoint,computer)
	response = rest_methods.patch(url, headers, body)
	if debug:
		log.write("** DEBUG: Isolate Affected Computer id: {} moved to new group\n".format(computer))
		


##  Get all "Threat Detected" events for defined group and type.  
##Get all Triage events for the group, instead of Isolated events.  This are endpoints where Threat Detected but no quarantine event happened.
###So lets investigate them further (Triage)
url = "https://{}:{}@{}/v1/events?group_guid[]={}&event_type[]={}".format(client_id,api_key,endpoint,group_id,triage_event_id)
if debug:
	log.write("** DEBUG: URL for request is :{}\n".format(url))
response = rest_methods.ampget(url)
affected_computers = []
for events in response["data"]:
	affected_computers.append(events["computer"]["connector_guid"])
	if debug:
		log.write ("** DEBUG: Affected Triage computer found based on event {}\n".format(events["computer"]["connector_guid"]))

##prune list for only unique values.  The set function iterates over the entire list & clears out any duplicates. 
unique_list = set(affected_computers)
if debug:
	for val in unique_list:
		log.write("** DEBUG: Triage Affected Computer id: {}\n".format(val))

###  ****  GET THE MAC ADDRESSES OF ALL INTERFACES OF EACH COMPUTER  *****
#Get the mac addresses of each computer in the unique_list.
for triage_computer in unique_list:
	url = "https://{}:{}@{}/v1/computers/{}".format(client_id,api_key,endpoint,triage_computer)
	response = rest_methods.ampget(url)
	#because computers may have more than one interface, network_addresses is an array.  This next for loop is to pull the mac address for each interface. 
	mac_addr = []
	for interface in response["data"]["network_addresses"]:
		mac_addr.append(interface["mac"])
		#print interface["mac"]
		log.write("** DEBUG: Triage Affected Computer mac_addr: {}\n".format(interface["mac"]))
	
	#   ********  Assign ANC Labels in ISE for Triage Computers *********
	#Trigger the ANC label assignment for Triage Computers to Investigate.  This is hard-coded for ANC-Investigate label in ISE. 
	for mac in mac_addr:
		body = {
		"OperationAdditionalData": {
		"additionalData": [{
		"name": "macAddress",
		"value": mac
		},
		{
		"name": "policyName",
		"value": "ANC-Investigate"
		}]
		}
		}
		url = "https://{}:{}@{}:{}/ers/config/ancendpoint/apply".format(username,password,host,port)
		response = rest_methods.put(url,headers,body)

#   ********  Move the Triage Computers into a new Group in AMP  *********
# ** Now that we have a list of computers which exhibit the Threat Detected event, but not a "Threat Quarantine" event.
#  We will move those into the Triage Group, in addition to assigning them the "ANC-Investigate" label that happened above.  

body = {"group_guid": triage_dest_group_id}
for computer in unique_list:
	url = "https://{}:{}@{}/v1/computers/{}".format(client_id,api_key,endpoint,computer)
	response = rest_methods.patch(url, headers, body)
	if debug:
		log.write("** DEBUG: Affected Computer id: {} move to new group\n".format(computer))

print "DONE ! - Thank you for using Aaron & Neil's RTC Script"
log.close()
