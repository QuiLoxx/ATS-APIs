#!/usr/bin/python
import connect
# ----------BEGIN : USER CONFIG VARIABLE SECTION----------

fmc_hostname = "neipatel-fmc"
fmc_username = "admin3"
fmc_password = "F!repowerl4b"
domain = "Global"
number_of_rules = 200
# ----------END : USER CONFIG VARIABLE SECTION----------



fmc = connect.fmc(fmc_hostname, fmc_username, fmc_password)
fmc.tokenGeneration(domain)

access_policy = {
  "type": "AccessPolicy",
  "name": "LARGE-ACP",
  "defaultAction": {
    "action": "BLOCK"
  }
}

policy_id = fmc.createPolicy(access_policy)


bulk_rules = []

while number_of_rules > 0:
    for num in range(1, 6):
        network = "1.1."+str(num)+"."+str(number_of_rules)
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
                    "value": network
                  }
                ]
            },
            "logBegin": False,
            "logEnd": True,
            "logFiles": False,
            "name": network + "to-any"
        }
        bulk_rules.append(access_rule)
    number_of_rules = number_of_rules - 1

fmc.createRule(bulk_rules, policy_id)

# use policy id to make rules after creation of objects is complete

cleanup = raw_input("Would you like to cleanup? [1/0]")
if bool(int(cleanup)) is not False:
    fmc.deletePolicy(policy_id)
