#!/usr/bin/python
import connect
import datetime
import time
# ----------BEGIN : USER CONFIG VARIABLE SECTION----------

fmc_hostname = ""
fmc_username = ""
fmc_password = ""
domain = "Global"
off_time_range = "16:00-08:00"
# ----------END : USER CONFIG VARIABLE SECTION----------

def makeRule(fmc, policy_id):
    access_rule = {
        "action": "ALLOW",
        "enabled": True,
        "type": "AccessRule",
        "sendEventsToFMC": True,
        "vlanTags": {},
        "sourceNetworks": {
            "literals": [
              {
                "type": "Network",
                "value": "10.1.1.0/24"
              }
            ]
        },
        "logBegin": False,
        "logEnd": True,
        "logFiles": False,
        "name": "10.1.1.0/24 to-any"
    }
    #create the inital rule, now that we have the initial rule lets turn it on and off
    rule_id = fmc.createRule(access_rule, policy_id)
    access_rule["id"]=rule_id
    return access_rule, rule_id

def disableRule(access_rule, policy_id, rule_id, fmc):
    access_rule["enabled"]=False
    fmc.patchRule(access_rule,policy_id,rule_id)

def enableRule(access_rule, policy_id, rule_id, fmc):
    access_rule["enabled"]=True
    fmc.patchRule(access_rule,policy_id,rule_id)

#create a connection to the FMC
fmc = connect.fmc(fmc_hostname, fmc_username, fmc_password)
fmc.tokenGeneration(domain)
#create an access policy
access_policy = {
  "type": "AccessPolicy",
  "name": "time-based-ACP",
  "defaultAction": {
    "action": "BLOCK"
  }
}
policy_id = fmc.createPolicy(access_policy)
#create an access rule
access_rule, rule_id = makeRule(fmc, policy_id)
#now that we have the rule in question lets turn it on or off based on time of day
#continuous loop running all the time looking at time of day
#clean up the time range
start_time = off_time_range.split("-")[0]
end_time = off_time_range.split("-")[1]

start_time = int(start_time.split(":")[0]+start_time.split(":")[1])
end_time = int(end_time.split(":")[0]+end_time.split(":")[1])

try:
    while True:
        print "STARTING TIME MONITOR TO QUIT PRESS CNTRL-C"
        now = datetime.datetime.now()
        timenow = int(str(now.hour).zfill(2) + str(now.minute).zfill(2))
        #figure out if time now is between the window defined
        if start_time > end_time:
            #print "over midnight"
            if timenow >= start_time or timenow <= end_time:
                #means time is inbetween so we disable the rule
                print "...currently in disable time, rule is disabled"
                disableRule(access_rule,policy_id,rule_id,fmc)

            else:
                #means time is not inbetween so we enable the rule
                print "...currently NOT in disable time, rule is enabled"
                enableRule(access_rule,policy_id,rule_id,fmc)
        else:
            #print "not over midnight"
            if timenow >= start_time and timenow <= end_time:
                #means time is inbetween so we disable the rule
                print "...currently in disable time, rule is disabled"
                disableRule(access_rule,policy_id,rule_id,fmc)
            else:
                #means time is not inbetween so we enable the rule
                print "...currently NOT in disable time, rule is enabled"
                enableRule(access_rule,policy_id,rule_id,fmc)

        #minute sleep, this can be changed as desired (10 minute granularity)
        #WARNING the token is regenerating  because there is 10 minute sleep
        fmc.tokenGeneration(domain)
        time.sleep(600)

except KeyboardInterrupt:
    print "ENDING TIME MONTIOR...THANK YOU FOR USING TIME BASED ACLS"
    pass
