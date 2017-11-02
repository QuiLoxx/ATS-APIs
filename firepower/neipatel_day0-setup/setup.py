#!/usr/bin/python
import connect
# ----------BEGIN : USER CONFIG VARIABLE SECTION----------

fmc_hostname = ""
fmc_username = ""
fmc_password = ""
device_name = ""
device_hostname = ""
regkey = "123456"
domain = "Global"

# ----------END : USER CONFIG VARIABLE SECTION----------

fmc = connect.fmc(fmc_hostname, fmc_username, fmc_password)
fmc.tokenGeneration(domain)

access_policy = {
  "type": "AccessPolicy",
  "name": "day0_policy",
  "defaultAction": {
    "action": "BLOCK"
  }
}

inside_network = {
  "name": "inside_network",
  "value": "192.168.10.0/24",
  "overridable": False,
  "description": "Inside Network Object",
  "type": "Network"
}

dmz_network = {
  "name": "dmz_network",
  "value": "192.168.20.0/24",
  "overridable": False,
  "description": "DMZ Network Object",
  "type": "Network"
}

server_network = {
  "name": "server_network",
  "value": "192.168.30.0/24",
  "overridable": False,
  "description": "Server Network Object",
  "type": "Network"
}

policy_id = fmc.createPolicy(access_policy)
inside_name, inside_network_id = fmc.createNetwork(inside_network)
dmz_name, dmz_network_id = fmc.createNetwork(dmz_network)
server_name, server_network_id = fmc.createNetwork(server_network)

access_rule = {
    "action": "ALLOW",
    "enabled": True,
    "type": "AccessRule",
    "sendEventsToFMC": True,
    "vlanTags": {},
    "sourceNetworks": {
        "objects": [
          {
            "type": "Network",
            "id": inside_network_id,
            "name": inside_name
          }
        ]
    },
    "destinationNetworks": {
        "objects": [
          {
            "type": "Network",
            "id": dmz_network_id,
            "name": dmz_name
          }
        ]
    },
    "logBegin": False,
    "logEnd": True,
    "logFiles": False,
    "name": "Inside to DMZ"
}

rule_id = fmc.createRule(access_rule, policy_id)

device_add = raw_input("Would you like to add a device? [1/0]")

if bool(int(device_add)) is not False:
    device = {
      "name": device_name,
      "hostName": device_hostname,
      "regKey": regkey,
      "type": "Device",
      "license_caps": [
        "BASE",
        "MALWARE",
        "URLFilter",
        "THREAT"
      ],
      "accessPolicy": {
        "id": policy_id,
        "type": "AccessPolicy"
      }
    }
    fmc.addDevice(device)

# use policy id to make rules after creation of objects is complete

cleanup = raw_input("Would you like to cleanup? [1/0]")
if bool(int(cleanup)) is not False:
    fmc.deletePolicy(policy_id)
    fmc.deleteNetwork(inside_network_id)
    fmc.deleteNetwork(dmz_network_id)
    fmc.deleteNetwork(server_network_id)
