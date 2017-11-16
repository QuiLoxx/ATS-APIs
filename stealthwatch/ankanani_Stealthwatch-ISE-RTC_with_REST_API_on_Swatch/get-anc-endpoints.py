import rest_methods
import json
from datetime import datetime

##Import variables to get configuration
config = json.loads(open("parameters.json").read())

##Set Variables for use
debug = config["debug"]
ISE_hostname = config["ISE_hostname"]
ISE_port = config["ISE_port"]
ISE_username = config["ISE_username"]
ISE_password = config["ISE_password"]

# output format either JSON or XML (json is default)
output_format = "json"

debug_log = open("debug_logfile.log", "a")
anc_endpoints_json = open ("anc_endpoints.json","w")
anc_endpoints_txt = open ("anc_endpoints.txt","a")

debug_log.write("\n\n##############################################\nTimestamp : " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n")
anc_endpoints_txt.write("\n\n##############################################\nTimestamp : " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n")

# build the headers based on input
# forcing the headers to be json, instead of XML for easier use
iseheaders = {
        "Content-Type": "application/json",
        "Accept": "application/json"
        }
if debug:
    debug_log.write("REQUEST HEADERS:{}\n".format(iseheaders))

# build the base URL for get-all anc ancendpoint configured in ISE.  ISE calls them ANC policies but that is a misnomber. 
iseurl = "https://{}:{}@{}:{}/ers/config/ancendpoint".format(ISE_username, ISE_password, ISE_hostname, ISE_port)
if debug:
    debug_log.write("BASE URL for policy IS:{}\n".format(iseurl))
endpoints = rest_methods.iseget(iseurl, iseheaders)

# THIS SECTION HANDLES THE OUTPUT OF JSON RESPONSE FOR THE ENDPOINTS
#print endpoints
json.dump(endpoints, anc_endpoints_json)

for endpoint in endpoints['SearchResult']['resources']:
	#print str(endpoint['id'])
	anc_endpoints_txt.write( str(endpoint['id']) + '\n')

