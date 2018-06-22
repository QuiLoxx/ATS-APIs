import security_center as sc
import threading
import subprocess
import time
import ConfigParser

configParser = ConfigParser.RawConfigParser()
configFilePath = r"config.cfg"
configParser.read(configFilePath)

username = configParser.get('UserVariables','username')
password = configParser.get('UserVariables','password')
address = configParser.get('UserVariables','address')
debug = configParser.getboolean('UserVariables', 'debug')
ip_range = configParser.get('UserVariables','ip_range')
page_size = configParser.getint('UserVariables', 'page_size')
fmc = configParser.get('UserVariables','fmc')
delay = configParser.getint('UserVariables', 'delay')
quiet = configParser.getboolean('UserVariables', 'quiet')
#debug variable for testing
staging = False
# loop variable
processing = True
# open csv for writing
csv = open("csvin.txt", "w")
csv.write("SetSource, SecurityCenter 5.x\n")

security_center = sc.SecurityCenter(address, debug=debug)
security_center.login(username,password,force_session=True)
#define the query so we know what we are looking for (on first run we are doing a full dump)
#inital call for getting latest vulnerability data (Only Run once)
query = {
        "type": "vuln",
        "tool": "vulndetails",
        "sourceType": "cumulative",
        "startOffset": 0,
        "endOffset": page_size,
        "filters":[
                {
                "id": "severity",
                "filterName": "severity",
                "operator":"=",
                "type": "vuln",
                "isPredefined": True,
                "value": "4,3,2,1"
                },
                {
                "id": "ip",
                "filterName": "ip",
                "operator":"=",
                "type": "vuln",
                "isPredefined": True,
                "value": ip_range.replace("\\n", "\n")
                }
            ]
        }
# build a host cache to elimiate redundant commands on the FMC
host_cache = []
while processing:
    response = security_center.getAnalysis(type="vuln", sourceType="cumulative", query=query)
    # process the page of data and write to the CSV
    for vulnerability in response["results"]:
        #logic in case vulnerability protocol is not supported
        if vulnerability["protocol"].lower() == "icmp":
            port = ""
            protocol = ""
        else:
            port = vulnerability["port"]
            protocol = vulnerability["protocol"].lower()
        if vulnerability["ip"] not in host_cache:
            # this means we are at a new host so we can write a host entry
            host_cache.append(vulnerability["ip"])
            csv.write("AddHost, {}\n".format(vulnerability["ip"]))
        #write the vulnerability to the csv for import
        csv.write("AddScanResult, {}, \"SecurityCenter 5.x\", {}, {}, {}, \"{}\", \"{}\", \"cve_ids: {}\", \"bugtraq_ids:\"\n".format(
        vulnerability["ip"],
        vulnerability["pluginID"],
        port,
        protocol,
        vulnerability["pluginName"],
        vulnerability["synopsis"],
        vulnerability["cve"].replace(","," ")))

    # Now that we have processed the page lets see if we need to do it all over again for a new page
    size = int(response["totalRecords"])
    page_start = int(response["startOffset"])
    page_end = int(response["endOffset"])
    returned = int(response["returnedRecords"])
    if page_end >= size:
        # this means there is only one page or this is the last page to process so we can finish processing
        csv.write("ScanFlush\n")
        csv.close()
        processing = False
    else:
        page_start = page_end
        page_end = page_end + page_size
        query["startOffset"] = page_start
        query["endOffset"] = page_end
if not staging:
    if debug:
        pipe = subprocess.call(["./sf_host_input_agent.pl", "-server={}".format(fmc), "-level=3","-plugininfo=csvin.txt", "csv" ])
    else:
        pipe = subprocess.call(["./sf_host_input_agent.pl", "-server={}".format(fmc), "-level=0","-plugininfo=csvin.txt", "csv" ])
processing = True
def updateVulns (SC, processing):
    csv = open("csvupdate.txt", "w")
    csv.write("SetSource, SecurityCenter 5.x\n")
    query = {
            "type": "vuln",
            "tool": "vulndetails",
            "sourceType": "cumulative",
            "startOffset": 0,
            "endOffset": page_size,
            "filters":[
                    {
                    "id": "severity",
                    "filterName": "severity",
                    "operator":"=",
                    "type": "vuln",
                    "isPredefined": True,
                    "value": "4,3,2,1"
                    },
                    {
                    "id": "ip",
                    "filterName": "ip",
                    "operator":"=",
                    "type": "vuln",
                    "isPredefined": True,
                    "value": ip_range
                    },
                    {
                    "id": "mitigatedStatus",
                    "filterName": "mitigatedStatus",
                    "operator":"=",
                    "type": "vuln",
                    "isPredefined": True,
                    "value": "previously"
                    },
                ]
            }
    while processing:
        response = SC.getAnalysis(type="vuln", sourceType="cumulative", query=query)
        # process the page of data and write to the CSV
        for vulnerability in response["results"]:
            #write the vulnerability to the csv for import
            csv.write("DeleteScanResult, {}, \"SecurityCenter 5.x\", {}, {}, {}\n".format(
            vulnerability["ip"],
            vulnerability["pluginID"],
            port,
            protocol))

        # Now that we have processed the page lets see if we need to do it all over again for a new page
        size = int(response["totalRecords"])
        page_start = int(response["startOffset"])
        page_end = int(response["endOffset"])
        returned = int(response["returnedRecords"])
        if page_end >= size:
            # this means there is only one page or this is the last page to process so we can finish processing
            csv.write("ScanFlush\n")
            csv.close()
            processing = False
        else:
            page_start = page_end
            page_end = page_end + page_size
            query["startOffset"] = page_start
            query["endOffset"] = page_end
    if not staging:
        if debug:
            pipe = subprocess.call(["./sf_host_input_agent.pl", "-server={}".format(fmc), "-level=3","-plugininfo=csvupdate.txt", "csv" ])
        else:
            pipe = subprocess.call(["./sf_host_input_agent.pl", "-server={}".format(fmc), "-level=0","-plugininfo=csvupdate.txt", "csv" ])

#start working on multiple threads
exitFlag = 0
class processThread (threading.Thread):
    def __init__(self, threadID, name,delay):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.delay = delay
    def run(self):
        print "Starting Vulnerability Update Thread"
        counter = 0
        try:
            while True:
                updateVulns(security_center,processing)
                counter += 1
                print "Ran update {} times @ {}".format(counter, time.ctime(time.time()))
                print "sleeping for {} minutes".format(str(float(delay/60)))
                time.sleep(delay)
        except KeyboardInterrupt:
            print "Terminating thread."
thread1 = processThread(1,"update vuln", delay)
thread1.start()
