import amp_api
import json
import sys

# Import variables to get configuration
config = json.loads(open("parameters.json").read())
log = open("debug.log", "w")
log.write("**debug - loading in parameters now....\n")
csv = open("hostinputcsv.txt", "w")
# Create dictionary of variables
var = {
    "debug": config["debug"],
    "client_id": config["client_id"],
    "api_key": config["api_key"],
    "endpoint": config["endpoint"],
    "group_name": config["group_name"],
    }

if var["debug"]:
    log.write("**debug - parameters loaded in.... OK!\n")
    log.write("**debug - begin parameter check....\n")
else:
    log.write("**debug - debug logging is disabled!\n")
# Check to make sure there is data in the parameters
for key, value in var.iteritems():
    if key == "debug":
        continue
    elif value != "":
        log.write("**debug - {} is {}.... OK!\n".format(key, value))
    else:
        log.write("**debug - {} is Blank.... FAIL!\n".format(key, value))
        print "MISSING - value for {}".format(key)
        sys.exit()
if var["debug"]:
    log.write("**debug - parameter check complete.... OK!\n")

amp = amp_api.amp(var["endpoint"], var["client_id"], var["api_key"])

group_data = amp.get("/v1/groups")
found = False
for group in group_data["data"]:
    if group["name"] == var["group_name"]:
        group_guid = group["guid"]
        found = True

if found and var["debug"]:
    log.write("**debug - group found with ID {}.... OK!\n".format(group_guid))
elif not found:
    print "FAIL - group name doesnt exist: {}".format(var["group_name"])
    sys.exit()

computers = amp.get("/v1/computers?group_guid[]={}".format(group_guid))
for computer in computers["data"]:
    hostname = computer["hostname"]
    os = computer["operating_system"].split(" ")
    for nic in computer["network_addresses"]:
        csv.write("AddHost, {}, {}\n".format(nic["ip"], nic["mac"]))
        if var["debug"]:
            log.write("**debug - new host added {} .... OK!\n".format(nic["ip"]))
        csv.write("SetOS, {}, Microsoft, {} {}\n".format(nic["ip"], os[0]+" "+os[1], " ".join(os[2:])))
        if var["debug"]:
            log.write("**debug - new os for host added {} .... OK!\n".format(nic["ip"]))

log.close()
csv.close()
