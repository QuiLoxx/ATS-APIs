import amp_api
import json
import sys
import subprocess
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
    "fmc": config["fmc"]
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
# automate getting the id if its at all related to vulnerable endpoints pull it out
event_types = amp.get("/v1/event_types")
for event in event_types["data"]:
    #this could be more intelligent right now it only gets the last one, doesnt matter because there is only one but could change
    if "Vulnerable" in event["name"]:
        event_type = event["id"]
csv.write("SetSource, AMP for Endpoints\n")
vul_id = 10024
for computer in computers["data"]:
    guid = computer["connector_guid"]
    hostname = computer["hostname"]
    os = computer["operating_system"].split(" ")
    if "Network" in os:
        continue
    for nic in computer["network_addresses"]:
        if os[0] != ("Android"):
            csv.write("AddHost, {}, {}\n".format(nic["ip"], nic["mac"]))
        if var["debug"] and os[0] != ("Android"):
            log.write("**debug - new host added {} .... OK!\n".format(nic["ip"]))
        if os[0] == ("Windows"):
            csv.write("SetOS, {}, Microsoft, {} {}\n".format(nic["ip"], os[0]+" "+os[1], " ".join(os[2:])))
        if os[0] == ("OSX"):
            csv.write("SetOS, {}, Mac, {} {}\n".format(nic["ip"], os[0]+" "+os[1], " ".join(os[2:])))
        # Remarked out. Android does not provide Network Address fields. Causes errors.
        #if os[0] == ("Android"):
        #    csv.write("SetOS, {}, Google, {} {}\n".format(nic["ip"], os[0]+" "+os[1], " ".join(os[2:])))
        if os[0] == ("Linux"):
            csv.write("SetOS, {}, Cent OS , {} {}\n".format(nic["ip"], os[0]+" "+os[1], " ".join(os[2:])))
        if var["debug"]:
            log.write("**debug - new os for host added {} .... OK!\n".format(nic["ip"]))
    #now that we wrote the host details for the device lets find any vulnerabilities
    cve = ""
    vulns = amp.get("/v1/events?connector_guid[]={}&event_type[]={}".format(guid,event_type))
    for vuln in vulns["data"]:
        for item in vuln["vulnerabilities"]:
            #this check needs to be  changed for python 3.x since it is only availible in 2.x
            if item.has_key("name"):
                name = item["name"] + item["version"]
            cve = cve + item["cve"] + " "
            split = item["cve"].split("-")
            cve_string = "cve_ids: {}".format(cve)
        csv.write("AddScanResult, {}, \"AMP for Endpoints\", {},,,{},,\"{}\", \"bugtraq_ids:\"\n".format(nic["ip"],vul_id,name,cve_string))
        vul_id = vul_id + 1
csv.write("ScanFlush")
csv.close()
# Call the Perl ref. client for the Host Input
pipe = subprocess.call(["./sf_host_input_agent.pl", "-server={}".format(var["fmc"]), "-level=3","-plugininfo=hostinputcsv.txt", "csv" ])

log.close()
