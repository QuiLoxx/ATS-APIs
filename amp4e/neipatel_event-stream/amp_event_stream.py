#!/user/bin/python

import amp_api
import json
import sys
import pika

# Import variables to get configuration
config = json.loads(open("parameters.json").read())
log = open("debug.log", "w")
log.write("**debug - loading in parameters now....\n")
# Create dictionary of variables
var = {
    "debug": config["debug"],
    "client_id": config["client_id"],
    "api_key": config["api_key"],
    "endpoint": config["endpoint"],
    "group_name": config["group_name"],
    "event_name": config["event_name"],
    "event_ids" : config["event_ids"],
    "event_choice" : config["id_or_name"]
    }

if var["debug"]:
    log.write("**debug - parameters loaded in.... OK!\n")
    log.write("**debug - begin parameter check....\n")
else:
    log.write("**debug - debug logging is disabled!\n")

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


if var["event_choice"] == "name":
    found = False
    event_list = amp.get("/v1/event_types")
    for event in event_list["data"]:
        if event["name"] == var["event_name"]:
            event_id = event["id"]
            found = True

    if found and var["debug"]:
        log.write("**debug - event type found with ID {}.... OK!\n".format(event_id))
    elif not found:
        print "FAIL - event type doesnt exist: {}".format(var["event_name"])
        sys.exit()

    body = {
        "name": "lab_event",
        "event_type": ["{}".format(event_id)],
        "group_guid": ["{}".format(group_guid)]
    }
if var["event_choice"] == "id":

    body = {
        "name": "lab_event",
        "event_type": var["event_ids"],
        "group_guid": ["{}".format(group_guid)]
    }
print body
event_stream = amp.post("/v1/event_streams", body)
if var["debug"]:
    log.write("**debug - event stream created.... OK!\n")
    log.write("**debug - begining work to start listening for events.... OK!\n")
print event_stream
print "---------"
url = "amqps://{}:{}@{}:{}".format(
            event_stream["data"]["amqp_credentials"]["user_name"],
            event_stream["data"]["amqp_credentials"]["password"],
            event_stream["data"]["amqp_credentials"]["host"],
            event_stream["data"]["amqp_credentials"]["port"]
            )
print url

parameters = pika.URLParameters(url)
connect = pika.BlockingConnection(parameters)
channel = connect.channel()

channel.queue_declare(queue=event_stream["data"]["amqp_credentials"]["queue_name"], passive=True)


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)


channel.basic_consume(callback,
                      queue=event_stream["data"]["amqp_credentials"]["queue_name"])
print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()

# remove event stream and confirm its gone right away for cleanup
response = amp.delete("/v1/event_streams/{}".format(str(stream_id)))
print response

response = amp.get("/v1/event_streams")
print response

# close all files that have been opened
log.close()
