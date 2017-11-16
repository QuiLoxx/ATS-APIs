import rest_methods
import json
from datetime import datetime, timedelta
import re
import time
import sys
import os.path

##  NOTES TO ANAND, AARON & NEIL  ##
### 11/1/17 - Setup script to handle pagination from AMP  
### 11/1/17 - Modify scripts to use the stream API for events in AMP
### 11/15/17 - Updated variable names for standardization across the other scripts
### 11/15/17 - Added code for Stealthwatch API. ISE code copied from AMP-RTC script with several modifications.


# *******  SETUP SECTION  ***********
if not os.path.exists("parameters.json"):
	print "ERROR: Could not find parameters.json file, hence exiting"
	sys.exit()
## Import variables to get configuration
config = json.loads(open("parameters.json").read())
debug = config["debug"]
ISE_hostname = config["ISE_hostname"]
ISE_port = config["ISE_port"]
ISE_username = config["ISE_username"]
ISE_password = config["ISE_password"]
SMC_hostname = config["SMC_hostname"]
SMC_username = config["SMC_username"]
SMC_password = config["SMC_password"]
SMC_tenant_id = config["SMC_tenant_id"]


debug_log = open("debug_logfile.log", "a")

debug_log.write("\n\n##############################################\nTimestamp : " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n")

## Setup Headers for ISE. ISE REST API does not require a cookie based authenticatoin
iseheaders = {
        "Content-Type": "application/json",
        "Accept": "application/json"
        }
## Authenticate to SMC and get the cookie
SMC_cookie = rest_methods.smcauth(SMC_hostname, SMC_username, SMC_password)
smcheaders = {
        "Content-Type": "application/json",
        "Cookie": SMC_cookie
        }

## Read the ANC Labels from the file that was created earlier by quering ISE. For the initial version, we are not using this part of the code, hence commenting it out
#if not os.path.exists("anc_labels.json"):
#	print "ERROR: Could not find 'anc_labels.json' file, hence exiting. Run the separate script 'get-anc-labels.py' to extract the ANC Labels in a separate file first"
#	if debug:
#		debug_log.write("** ERROR: Could not find 'anc_labels.json' file, hence exiting. Run the separate script 'get-anc-labels.py' to extract the ANC Labels in a separate file first\n\n")
#	sys.exit()
#anc_labels = json.loads(open("anc_labels.json").read())

## Read the Stealthwatch Security Events from the file that was created earlier by quering Stealthwatch SMC
if not os.path.exists("stealthwatch_security_events-list.txt"):
	print "ERROR: Could not find 'stealthwatch_security_events-list.txt' file, hence exiting. Run the separate script 'get-stealthwatch-security-event-list.py' to extract the Stealthwatch Security Event IDs in a separate file first and then select the Security Event IDs in that file for which you want to enable automatic ANC through this script"
	if debug:
		debug_log.write("** ERROR: Could not find 'stealthwatch_security_events-list.txt' file, hence exiting. Run the separate script 'get-stealthwatch-security-event-list.py' to extract the Stealthwatch Security Event IDs in a separate file first and then select the Security Event IDs in that file for which you want to enable automatic ANC through this script\n\n")
	sys.exit()
stealthwatch_security_events_list_full = open("stealthwatch_security_events-list.txt").read().splitlines()

## Extract the ids of specific Security Events that needs to be queried in SMC
stealthwatch_security_events_list_to_be_queried = []
for line in stealthwatch_security_events_list_full:
	#print line
	match = re.search(r"^(\d+) -- (.*)$",line)
	if match:
		stealthwatch_security_events_list_to_be_queried.append(match.group(1))
if debug:
	debug_log.write("** DEBUG: List of the ids of specific Security Events that needs to be queried in SMC : {}\n\n".format(stealthwatch_security_events_list_to_be_queried))
#print stealthwatch_security_events_list_to_be_queried
if len(stealthwatch_security_events_list_to_be_queried) == 0:
	print "ERROR: Atleast 1 security Event needs to be specified in the list to be queried. Currently NO event ids are provided, hence exiting."
	if debug:
		debug_log.write("** ERROR: Atleast 1 security Event needs to be specified in the list to be queried. Currently NO event ids are provided, hence exiting\n\n")
	sys.exit()

## Create a query for the selected security events
smcurl = "https://{}/sw-reporting/v1/tenants/{}/security-events/queries".format(SMC_hostname,SMC_tenant_id)
time_to = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
time_from = (datetime.utcnow() - timedelta(hours = 1)).strftime('%Y-%m-%dT%H:%M:%SZ')
body = {
  "securityEventTypeIds": stealthwatch_security_events_list_to_be_queried,
  "timeRange": {
    "from": time_from,
    "to": time_to
  }
}
#print body
if debug:
	debug_log.write("** DEBUG: Sending the Following Query to the SMC : {} -- {} -- {}\n\n".format(smcurl,smcheaders,body))
smcresponse = rest_methods.smcpost(smcurl, smcheaders, body)
#print smcresponse
smcqueryid = smcresponse['data']['searchJob']['id']
smcqueryJobStatus = smcresponse['data']['searchJob']['searchJobStatus']
print "Query ID: " + smcqueryid + " : " + smcqueryJobStatus
if debug:
	debug_log.write("** DEBUG: Query Response from the SMC : {}\n\n".format(smcresponse))

## Poll the SMC to check the status of the Query Job
while True:
	print "Checking the status of the query every 5 seconds"
	time.sleep(5)
	smcurl = "https://{}/sw-reporting/v1/tenants/{}/security-events/queries/{}".format(SMC_hostname,SMC_tenant_id,smcqueryid)
	if debug:
		debug_log.write("** DEBUG: Sending the Following Query to the SMC : {} -- {} -- {}\n\n".format(smcurl,smcheaders,body))
	smcresponse = rest_methods.smcget(smcurl, smcheaders)
	if debug:
		debug_log.write("** DEBUG: Query Response from the SMC : {}\n\n".format(smcresponse))
	smcqueryJobStatus = smcresponse['data']['status']
	print "Query ID: " + smcqueryid + " : " + smcqueryJobStatus
	if smcqueryJobStatus == "COMPLETED":
		print "Query Job Completed. Lets check the result"
		if debug:
			debug_log.write("** DEBUG: Sending the Following Query to the SMC : {} -- {} -- {}\n\n".format(smcurl,smcheaders,body))
		smcurl = "https://{}/sw-reporting/v1/tenants/{}/security-events/results/{}".format(SMC_hostname,SMC_tenant_id,smcqueryid)
		smcresponse = rest_methods.smcget(smcurl, smcheaders)
		if debug:
			debug_log.write("** DEBUG: Query Response from the SMC : {}\n\n".format(smcresponse))
		break
	if smcqueryJobStatus == "FAILED":
		print "Job Failed"
		break
if debug:
	debug_log.write("** DEBUG: Result of Query for Security Events to the SMC is : {}\n\n".format(smcresponse))

## Extract the Source/Target IP Addresses from the Security Events
## This code can be modified in the future depending on the Alarm
print "Extract the Source/Target IP Addresses from the Security Events"
ip_addresses_of_interesting_endpoints = []
for security_event in smcresponse['data']['results']:
	#print security_event
	if 'target' in security_event and 'ipAddress' in security_event['target']:
		ip_addresses_of_interesting_endpoints.append(security_event['target']['ipAddress'])
	if 'source' in security_event and 'ipAddress' in security_event['source']:
		ip_addresses_of_interesting_endpoints.append(security_event['source']['ipAddress'])
ip_addresses_of_interesting_endpoints = list(set(ip_addresses_of_interesting_endpoints))
#print ip_addresses_of_interesting_endpoints
print "Found total " + str(len(ip_addresses_of_interesting_endpoints)) + " Unique IP addresses in the Security Events"
if debug:
	debug_log.write("** DEBUG: List of all Unique IP addresses extracted from all the security events is : {}\n\n".format(ip_addresses_of_interesting_endpoints))

## Remove non RFC 1918 addresses to ensure that you are not ANC'ing any Public IP Address
## ANC'ing Public IP Addresses will have no effect assuming that all endpoints are having only private RFC 1918 addresses
print "Remove non RFC 1918 addresses to ensure that you are not ANC'ing any Public IP Address"
final_ip_addresses_of_interesting_endpoints = []
for ipaddress in ip_addresses_of_interesting_endpoints:
	match = re.search("^(?:10|172\.(?:1[6-9]|2[0-9]|3[01])|192\.168)\..*",ipaddress)
	if match:
		final_ip_addresses_of_interesting_endpoints.append(ipaddress)
#print final_ip_addresses_of_interesting_endpoints
print "Found total " + str(len(final_ip_addresses_of_interesting_endpoints)) + " Unique RFC 1918 IP addresses in the Security Events"
if debug:
	debug_log.write("** DEBUG: Final List of RFC 1918 addresses that can be ANC'ed in ISE is : {}\n\n".format(final_ip_addresses_of_interesting_endpoints))

##  Assign the ANC Label to the Endpoints. This is hard-coded for "ANC-KickFromNetwork" label for this version of the script
print "Starting ANC Policy assignment for each IP address one-by-one"
print "Note that ANC Policy assignment can fail if either the session does not exist in ISE or same ANC policy is already assigned to an endpoint, with the assumption that other possibilities like ISE availability are all fine"
for ipAddress in final_ip_addresses_of_interesting_endpoints:
	body = {
	"OperationAdditionalData": {
	"additionalData": [{
	"name": "ipAddress",
	"value": ipAddress
	},
	{
	"name": "policyName",
	"value": "ANC-KickFromNetwork"
	}]
	}
	}
	iseurl = "https://{}:{}@{}:{}/ers/config/ancendpoint/apply".format(ISE_username, ISE_password, ISE_hostname, ISE_port)
	if debug:
		debug_log.write("** DEBUG: Sending the Following ANC Query to ISE : {}\n\n".format(iseurl))
	iseresponse = rest_methods.iseput(iseurl,iseheaders,body)
	if iseresponse == "Null":
		print ipAddress + " - ANC policy assignment succeeded"
		if debug:
			debug_log.write("** DEBUG: {} - ANC policy assignment succeeded. Got the Following Response from ISE : {}\n\n".format(ipAddress,iseresponse))
	else:
		print ipAddress + " - ANC policy assignment failed"
		if debug:
			debug_log.write("** DEBUG: {} - ANC policy assignment failed. Got the Following Response from ISE : {}\n\n".format(ipAddress,iseresponse))

print "\nDONE ! - Thank you for using Anand, Aaron & Neil's Stealthwatch RTC Script"
debug_log.close()
