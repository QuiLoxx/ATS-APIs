#!/usr/bin/env python
from securitycenter import SecurityCenter5
import json
import subprocess
import urllib3
if __name__ == '__main__':
	#surpress warnings
	urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
	parameters = json.loads(open("parameters.json").read())
	log = open("debug.log", "w")
	csv = open("csvin.txt", "w")
	csv.write("SetSource, Security Center\n")
	HOSTNAME = parameters["hostname"]
	USERNAME = parameters["username"]
	FMC = parameters["FMCHostname"]
	PASSWORD = parameters["password"]
	DEBUG = parameters["debug"]
	NETWORK = parameters["netrange"]
	ADDHOSTS = parameters["addHosts"]
	if DEBUG:
		log.write("**DEBUG: PARAMETERS READ IN \nHostname: {} \nUsername: {}\nPassword: {}\nNetwork: {}\n".format(HOSTNAME,USERNAME,PASSWORD,NETWORK))

	sc = SecurityCenter5(HOSTNAME)
	sc.login(USERNAME,PASSWORD, True)
	details = sc.analysis(('ip', '=', NETWORK), tool='sumid', page=0, page_size=1000, sortDir='desc',sortField='severity')
	for item in details:
		plugin_id = item["pluginID"]
		status = item["family"]["type"]
		severity = item["severity"]["description"]
		if status == "active" and severity != "Informative":
			vulnerable_hosts = sc.analysis(('ip', '=', NETWORK), ('pluginID', '=', str(plugin_id)), tool='vulndetails')
			for host in vulnerable_hosts:
				cves = host["cve"].replace(","," ")
				if ADDHOSTS:
					line_a = "AddHost,{}\n".format(host["ip"])
				#pruning for valid host protocol
				if host["protocol"] != "UDP" and host["protocol"] != "TCP":
					protocol = ""
				else:
					protocol = host["protocol"].lower()
				#Reference format: AddScanResult, ipaddr, scanner_id, vuln_id, port, protocol, name, description, cve_ids, bugtraq_ids
				line_b = "AddScanResult,{},\"Security Center\",{},{},\"{}\",\"{}\",\"{}\",\"cve_ids: {}\",\"bugtraq_ids:\"\n".format(host["ip"],plugin_id,host["port"],protocol,host["pluginName"],host["synopsis"],cves)
				if ADDHOSTS:
					csv.write(line_a)
				csv.write(line_b)
			if DEBUG:
				log.write("**DEBUG: Processed Vulnerability ID {} - {}\n".format(plugin_id, item["name"]))
				print "**DEBUG: Processed Vulnerability ID {} - {}\n".format(plugin_id, item["name"])
	csv.write("ScanFlush\n")
	csv.close()
	sc.logout
	csv.close()
	# Call the Perl ref. client for the Host Input
	pipe = subprocess.call(["./sf_host_input_agent.pl", "-server={}".format(FMC), "-level=3","-plugininfo=csvin.txt", "csv" ])
