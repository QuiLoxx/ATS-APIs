#!/usr/bin/env python

## Add your variables here

LOG_FILE = 'swalerts_logfile.log'
HOST, PORT = "0.0.0.0", 514
LIST_OF_STEALTHWATCH_ALARMS_TO_BE_CONSIDERED_FOR_ISE_AUTO_REMEDIATION = ['Bad Host','CSE: Employees to BlackHole High Traffic']
ISE_HOSTNAME = 'ise.mango.local'
ISE_ADMIN_USERNAME = 'admin'
ISE_ADMIN_PASSWORD = 'M1ngo@123'

#############################################################################################################################
#############################################################################################################################

## THIS IS A MULTI-THREADED SERVER THAT WILL LISTEN TO SYSLOG ALARMS FROM STEALTHWATCH SMC. WHEN IT RECEIVES SYSLOGS IT FIRST SAVES THEM IN A FILE, ANOTHER THREAD PARSES AND LOOKS FOR SPECIFIC ALARMS FOR WHICH THE USER WANTS ISE BASED AUTO-REMEDIATION.
## ON FINDING SUCJH ALARMS, IT EXTRACTS THE SOURCE IP ADDRESS FOR THOSE ALARMS AND SENDS ANC REQUEST TO ISE FOR THAT IP ADDRESS.

## NOTE THAT YOU WILL HAVE TO CONFIGURE SMC TO SEND SYSLOG TO THE HOST RUNNING THIS SCRIPT WHEN A PARTICULAR ALARM IS FIRED. 

## TO CONFIGURE THIS IN SMC. OPEN THE JAVA SWING CLIENT OF SMC. NAVIGATE TO CONFIGURATION -> RESPONSE MANAGEMENT -> RULES. ADD A NAME AND SELECT ENABLE. SELECT THE RULE AS - ALL SEVERITY INFORMATIONAL OR HIGHER.
## MOVE TO ACTION. CLICK ON ADD -> ADD -> PROVIDE IP ADDRESS OF THE HOST WHERE YOU ARE GOING TO RUN THIS SCRIPT. CLICK ON SYSLOG FORMATS -> ADD -> PUT THE BELOW TEMPLATE WITHOUT THE HASH IN THE BEGINNING, GIVE IT A NAME AND SAVE IT.SAVE EVERYTHING AND CLOSE.
#Lancope|StealthWatch|Notification:{alarm_type_id}|{alarm_type_name}|{alarm_severity_id}| alarm_desc="{alarm_type_description}" details="{details}" dst={target_ip}  src={source_ip}  start={start_active_time}  end={end_active_time}  cat={alarm_type_name} Alarm_ID={alarm_id} Source_HG={source_host_group_names} Target_HG={target_host_group_names} Source_HostSnapshot={source_url} Target_HostSnapshot={target_url} dpt={port} proto={protocol} FC_Name={device_name} FC_IP={device_ip} Domain={domain_id} tcn={target_country_name} scn={source_country_name} alarmsev={alarm_severity_name} alarmstatus={alarm_status}

## NOW YOU ARE READY TO RUN THIS SCRIPT.

import logging
import SocketServer
import threading
import re
import jsonpickle
import pprint
import time
import sys
import json
import requests
import os
import rest_methods
from datetime import datetime, timedelta

# class for Server Threads
class myThread (threading.Thread):
	def __init__(self, threadID, name, functionToStart):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.functionToStart = functionToStart
	def run(self):
		print "Starting %s" % (self.name)
		if self.functionToStart == 'start_syslog_server':
			try:
				start_syslog_server()
			except:
				raise
		elif self.functionToStart == 'start_syslog_watchdog_and_ise_mitigation':
			try:
				start_syslog_watchdog_and_ise_mitigation()
			except:
				raise

# call ISE ANC API
def call_ise_anc_api(ipAddress):
	iseheaders = {
        "Content-Type": "application/json",
        "Accept": "application/json"
        }
	print "Note that ANC Policy assignment can fail if either the session does not exist in ISE or same ANC policy is already assigned to an endpoint, with the assumption that other possibilities like ISE availability are all fine"
	print "Assign the ANC Label to the Endpoints. This is hard-coded for \"ANC-KickFromNetwork\" label for this version of the script\n"
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
	iseurl = "https://{}:{}@{}:{}/ers/config/ancendpoint/apply".format(ISE_ADMIN_USERNAME, ISE_ADMIN_PASSWORD, ISE_HOSTNAME, 9060)
	iseresponse = rest_methods.iseput(iseurl,iseheaders,body)
	if iseresponse == "Null":
		return "Successful"
	else:
		return "failed"


# class for UDP Syslog listener
logging.basicConfig(level=logging.INFO, format='%(message)s', datefmt='', filename=LOG_FILE, filemode='a')
class SyslogUDPHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		data = bytes.decode(self.request[0].strip())
		socket = self.request[1]
		syslog_message = str(data)
		logging.info(syslog_message)

# Start syslog Server main function
def start_syslog_server():
	try:
		server = SocketServer.UDPServer((HOST,PORT), SyslogUDPHandler)
		server.serve_forever(poll_interval=0.1)
	except:
		raise

# Start ISE Mitigation Watchdog main function
def start_syslog_watchdog_and_ise_mitigation():
	syslog_file = open(LOG_FILE, 'r')
	
	# maintain a file of alarm ids that are already addressed by this script through ANC to avoid duplicate ANC requests for the same alarm
	already_addressed_alarm_ids = []
	if os.path.exists("alarms_addressed_by_anc.log"):
		with open("alarms_addressed_by_anc.log", 'r') as alarms_addressed_logfile:
			for line in alarms_addressed_logfile:
				match = re.search(r"Alarm-id - ([a-zA-Z0-9:._\s-]+),",line)
				if match and match.group(1) not in already_addressed_alarm_ids:
					already_addressed_alarm_ids.append(match.group(1))

	alarms_addressed_logfile = open("alarms_addressed_by_anc.log", 'a')
	
	while True:
		new = syslog_file.readline()
		if new:
			data = parse_syslog_message(new)
			if data['alarm_type_name'] in LIST_OF_STEALTHWATCH_ALARMS_TO_BE_CONSIDERED_FOR_ISE_AUTO_REMEDIATION and data['alarm_id'] not in already_addressed_alarm_ids:
				print "\n-------\nAlarm-Name - %s \nAlarm-id - %s \nEndpoint IP - %s \nAlarm Timestamp - %s" % (data['alarm_type_name'],data['alarm_id'],data['start_active_time'],data['source_ip'])
				print "Host Groups for the Alarming IP - %s" % (data['source_host_group_names'])
				match = re.search(r"^([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)$",data['source_ip'])
				if match:
					ise_anc_status_message = call_ise_anc_api( data['source_ip'] )
					if ise_anc_status_message == "Successful":
						print "ANC Status - SUCCESSFUL\n"
						alarms_addressed_logfile.write("Alarm-Name - %s, Alarm-id - %s, Endpoint IP - %s, Alarm Timestamp - %s, ANC Status - SUCCESSFUL\n" % (data['alarm_type_name'],data['alarm_id'],data['start_active_time'],data['source_ip']))
					else:
						print "ANC Status - FAILED\n"
						alarms_addressed_logfile.write("Alarm-Name - %s, Alarm-id - %s, Endpoint IP - %s, Alarm Timestamp - %s, ANC Status - FAILED\n" % (data['alarm_type_name'],data['alarm_id'],data['start_active_time'],data['source_ip']))
		else:
			time.sleep(0.5)

# Parsing Raw Syslogs to Extract Fields as per the pre-defined template
def parse_syslog_message(syslog_message):
	data = dict()
	
	# Syslog format defined in Stealthwatch
	# Lancope|StealthWatch|Notification:{alarm_type_id}|{alarm_type_name}|{alarm_severity_id}| alarm_desc="{alarm_type_description}" details="{details}" dst={target_ip}  src={source_ip}  start={start_active_time}  end={end_active_time}  cat={alarm_type_name} Alarm_ID={alarm_id} Source_HG={source_host_group_names} Target_HG={target_host_group_names} Source_HostSnapshot={source_url} Target_HostSnapshot={target_url} dpt={port} proto={protocol} FC_Name={device_name} FC_IP={device_ip} Domain={domain_id} tcn={target_country_name} scn={source_country_name} alarmsev={alarm_severity_name} alarmstatus={alarm_status}
	
	match = re.search(r"Lancope\|StealthWatch\|Notification:([0-9]+)\|([a-zA-Z0-9:,._\s-]+)\|([0-9]+)\| alarm_desc=\"([^\"]*)\" details=\"([^\"]*)\" dst=([a-zA-Z0-9:._\s-]*) src=([a-zA-Z0-9:._\s-]*) start=([a-zA-Z0-9:._\s-]*) end=([a-zA-Z0-9:._\s-]*) cat=([a-zA-Z0-9:._\s-]*) Alarm_ID=([a-zA-Z0-9:._\s-]+) Source_HG=([a-zA-Z0-9:,._\s-]*) Target_HG=([a-zA-Z0-9:,._\s-]*) Source_HostSnapshot=([a-zA-Z0-9:,._\/#?\s-]*) Target_HostSnapshot=([a-zA-Z0-9:,._\/#?\s-]*) dpt=([a-zA-Z0-9,:._\s-]*) proto=([a-zA-Z0-9,:._\s-]*) FC_Name=([a-zA-Z0-9._\s-]*) FC_IP=([0-9.]*) Domain=([0-9]+) tcn=([a-zA-Z0-9:,._\s-]*) scn=([a-zA-Z0-9:,._\s-]*) alarmsev=([a-zA-Z0-9]*) alarmstatus=([a-zA-Z0-9]*)",syslog_message)
	if match:
		data['alarm_type_id'] = match.group(1)
		data['alarm_type_name'] = match.group(2)
		data['alarm_severity_id'] = match.group(3)
		data['alarm_type_description'] = match.group(4)
		data['details'] = match.group(5)
		data['target_ip'] = match.group(6)
		data['source_ip'] = match.group(7)
		data['start_active_time'] = match.group(8)
		data['end_active_time'] = match.group(9)
		data['cat'] = match.group(10)
		data['alarm_id'] = match.group(11)
		data['source_host_group_names'] = match.group(12)
		data['target_host_group_names'] = match.group(13)
		data['source_url'] = match.group(14)
		data['target_url'] = match.group(15)
		data['port'] = match.group(16)
		data['protocol'] = match.group(17)
		data['FC_name'] = match.group(18)
		data['FC_ip'] = match.group(19)
		data['domain_id'] = match.group(20)
		data['target_country_name'] = match.group(21)
		data['source_country_name'] = match.group(22)
		data['alarm_severity_name'] = match.group(23)
		data['alarm_status'] = match.group(24)
	return data


if __name__ == "__main__":
	# Create new threads
	thread1 = myThread(1, "Syslog Server Collector Thread", 'start_syslog_server')
	try:
		thread1.daemon = True
		thread1.start()
	except:
		raise
	
	thread2 = myThread(2, "Syslog Monitor and ISE Mitigation Thread", 'start_syslog_watchdog_and_ise_mitigation')
	try:
		thread2.daemon = True
		thread2.start()
	except:
		raise
	
	while True:
		try:
			time.sleep(1)
		except(KeyboardInterrupt, SystemExit):
			sys.exit()
