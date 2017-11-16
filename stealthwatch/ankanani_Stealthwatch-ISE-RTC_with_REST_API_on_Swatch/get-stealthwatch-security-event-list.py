import rest_methods
import json
from datetime import datetime

##Import variables to get configuration
config = json.loads(open("parameters.json").read())

##Set Variables for use
debug = config["debug"]
SMC_hostname = config["SMC_hostname"]
SMC_username = config["SMC_username"]
SMC_password = config["SMC_password"]
SMC_tenant_id = config["SMC_tenant_id"]

# output format either JSON or XML (json is default)
output_format = "json"

debug_log = open("debug_logfile.log", "a")
stealthwatch_security_events_json = open ("stealthwatch_security_events-list.json","w")
stealthwatch_security_events_txt = open ("stealthwatch_security_events-list.txt","w")

debug_log.write("\n\n##############################################\nTimestamp : " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n")
stealthwatch_security_events_txt.write("\n\n##############################################\nTimestamp : " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n")
stealthwatch_security_events_txt.write("README : MANUALLY UNCOMMENT THE SECURITY EVENTS FROM THE OUTPUT OF THIS PROGRAM FOR WHICH YOU WANT THE SOURCE IP ADDRESS TO BE ANCed\n\n")

SMC_cookie = rest_methods.smcauth(SMC_hostname, SMC_username, SMC_password)

# build the headers based on input
# forcing the headers to be json, instead of XML for easier use
smcheaders = {
        "Content-Type": "application/json",
        "Cookie": SMC_cookie
        }

# build the base URL for get-all anc labels configured in ISE.  ISE calls them ANC policies but that is a misnomber. 
smcurl = "https://{}/sw-reporting/v1/tenants/{}/security-events/templates".format(SMC_hostname,SMC_tenant_id)
if debug:
    debug_log.write("BASE URL for policy IS:{}\n".format(smcurl))
security_events_list = rest_methods.smcget(smcurl, smcheaders)

# THIS SECTION HANDLES THE OUTPUT OF JSON RESPONSE FOR THE SECURITY EVENTS
#print security_events_list
json.dump(security_events_list, stealthwatch_security_events_json)

for security_event in security_events_list['data']:
	#print str(security_event['id']) + ' -- ' + security_event['name']
	stealthwatch_security_events_txt.write( "#" + str(security_event['id']) + ' -- ' + security_event['name'] + '\n')
