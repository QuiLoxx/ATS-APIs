import rest_methods
import json

##Import variables to get configuration
config = json.loads(open("parameters.json").read())
log = open ("debug.log","w")


##Set Variables for use
host = config["host"]
port = config["port"]
username = config["username"]
password = config["password"]

# output format either JSON or XML (json is default)
output_format = "json"
debug = True

debug_log = open("logfile.log", "w")
anc_endpoints = open ("anc_endpoints.json","w")
anc_labels = open ("anc_labels.json","w")

# build the headers based on input
#forcing the headers to be json, instead of XML for easier use 

headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
        }
if debug:
    debug_log.write("REQUEST HEADERS:{}\n".format(headers))

# build the base URL for get-all endpoints with anc labels assigned
url = "https://{}:{}@{}:{}/ers/config/ancendpoint".format(username, password, host, port)
if debug:
    debug_log.write("BASE URL for endpoints IS:{}\n".format(url))

endpoints = rest_methods.get(url, headers)

# THIS SECTION HANDLES THE OUTPUT OF JSON RESPONSE FOR THE ENDPOINTS
print endpoints
json.dump(endpoints, anc_endpoints)

