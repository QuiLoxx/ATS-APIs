***Threat Grid Intelligence Feed Fetcher***

**Summary**

This tool fetches threat intelligence data feeds from the Threat Grid API.

**Files**

*TGIFF.py*
This is the script that reads optional arguments and the configuration file, and fetches the requested datafeed.

*TGIFF.cfg*
This is the configuration file that tells the script what server to connect to and what requests to make, etc. This will need to be updated if the API changes.

**Dependencies**
```
import logging, requests, sys, configparser, datetime, argparse
```

**Usage**

TGIFF takes parameters from the command line and from a configuration file, and constructs an API query to retrieve the feed as requested. The feed is printed to stdout (or to a specified optional file) exactly as received.

```
usage: TGIF.py [-h] [-a AFTER_TIME] [-b BEFORE_TIME] [-c CFG_FILE] [-e]
               [-k API_KEY] [-l LOG_FILE] [-m] [-o OUT_FILE] [-p PARAMETERS]
               [-s SERVER_NAME] [--rtfm] [-v]
               [feedName]

TGIF: Threat Grid Intelligence Feeds

positional arguments:
  feedName              specify the desired feed

optional arguments:
  -h, --help            show this help message and exit
  -a AFTER_TIME, --after_time AFTER_TIME
                        Specify a start time for the feed window. You want the
                        data from after this time. Must be in format
                        "%Y-%m-%dT%H:%M:%SZ". (default one hour ago, or one
                        hour before before_time if specified)
  -b BEFORE_TIME, --before_time BEFORE_TIME
                        Specify an end time for the feed window. You want the
                        data from before this time. Must be in format
                        "%Y-%m-%dT%H:%M:%SZ". (default now, or one hour after
                        after_time if specified)
  -c CFG_FILE, --cfg_file CFG_FILE
                        specify a configuration file (default TGIF.cfg))
  -e, --experiment      Do everything except request the feed. Most useful
                        with -v
  -k API_KEY, --api_key API_KEY
                        specify an API key value (overrides config file)
  -l LOG_FILE, --log_file LOG_FILE
                        specify a log file (overrides config file)
  -m, --feed_menu       print out the menu of available feeds in the config
                        file (not from the API) and exit
  -o OUT_FILE, --out_file OUT_FILE
                        specify an output file (default STDOUT)
  -p PARAMETERS, --parameters PARAMETERS
                        specify additional parameters as a single string TODO
  -s SERVER_NAME, --server_name SERVER_NAME
                        specify a server hostname (overrides config file)
  --rtfm                print a link to the API documentation for the
                        specified feed and exit (Threat Grid account required)
                        If no feed is specified it will print out links for
                        all feed types
  -v, --verbose         print diagnostic and troubleshooting information to
                        stdout

This script can be used to retrieve threat intel feeds from the Cisco Threat
Grid API. It reads configuration paramaters from the command line, and
defaults from a configuration file. Usage of this script requires a valid API
key. This utility is provided as an example, with no guarantees or support
options.

```
