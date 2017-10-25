#!/usr/bin/python
import requests
import json
import sys
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class fmc (object):
    """Class to define the FMC.

    Attributes
    Host: FMC hostname (FQDN OR IP)
    Username: FMC Username for API user
    Password: FMC Password for API user

    """

    def __init__(self, host, username, password):
        """Return FMC object whose attributes are host, username and password.

        init
        """
        self.host = host
        self.username = username
        self.password = password
        self.headers = {'Content-Type': 'application/json'}
        self.uuid = ""

    def tokenGeneration(self, domain):
        """Generate token."""
        path = "/api/fmc_platform/v1/auth/generatetoken"
        server = "https://"+self.host
        url = server + path
        try:
            r = requests.post(url, headers=self.headers, auth=requests.auth.HTTPBasicAuth(self.username, self.password), verify=False)
            auth_headers = r.headers
            token = auth_headers.get('X-auth-access-token', default=None)
            domains = auth_headers.get('DOMAINS', default=None)
            domains = json.loads("{\"domains\":" + domains + "}")
            for item in domains["domains"]:
                if item["name"] == domain:
                    self.uuid = item["uuid"]
                else:
                    print "ERROR:UUID NOT FOUND FOR SPECIFIED DOMAIN"
            if token is None:
                    print("No Token found, I'll be back terminating....")
                    sys.exit()
        except Exception as err:
            print ("Error in generating token --> " + str(err))
            sys.exit()
        self.headers['X-auth-access-token'] = token

    def createPolicy(self, data):
        """Create access policy with data given."""
        path = "/api/fmc_config/v1/domain/" + self.uuid + "/policy/accesspolicies"
        server = "https://"+self.host
        url = server + path
        try:
            r = requests.post(url, data=json.dumps(data), headers=self.headers, verify=False)
            status_code = r.status_code
            resp = r.text
            json_response = json.loads(resp)
            print("status code is: " + str(status_code))
            if status_code == 201 or status_code == 202:
                print "Post was sucessfull..."
            else:
                r.raise_for_status()
                print "error occured in POST -->" + resp
            return json_response["id"]
        except requests.exceptions.HTTPError as err:
            print ("Error in connection --> " + str(err))
        finally:
            if r:
                r.close()

    def createNetwork(self, data):
        """Create network with data given."""
        path = "/api/fmc_config/v1/domain/" + self.uuid + "/object/networks"
        server = "https://"+self.host
        url = server + path
        try:
            r = requests.post(url, data=json.dumps(data), headers=self.headers, verify=False)
            status_code = r.status_code
            resp = r.text
            json_response = json.loads(resp)
            print("status code is: " + str(status_code))
            if status_code == 201 or status_code == 202:
                print "Post was sucessfull..."
            else:
                r.raise_for_status()
                print "error occured in POST -->" + resp
            return json_response["name"], json_response["id"]
        except requests.exceptions.HTTPError as err:
            print ("Error in connection --> " + str(err))
        finally:
            if r:
                r.close()

    def createRule(self, data, policy_id):
        """Create rule with data given."""
        path = "/api/fmc_config/v1/domain/" + self.uuid + "/policy/accesspolicies/" + policy_id + "/accessrules?bulk=true"
        server = "https://"+self.host
        url = server + path
        try:
            r = requests.post(url, data=json.dumps(data), headers=self.headers, verify=False)
            status_code = r.status_code
            resp = r.text
            json_response = json.loads(resp)
            print("status code is: " + str(status_code))
            if status_code == 201 or status_code == 202:
                print "Post was sucessfull..."
            else:
                r.raise_for_status()
                print "error occured in POST -->" + resp
            return True
        except requests.exceptions.HTTPError as err:
            print ("Error in connection --> " + str(err))
        finally:
            if r:
                r.close()

    def deleteNetwork(self, data):
        """Delete network with data given."""
        path = "/api/fmc_config/v1/domain/" + self.uuid + "/object/networks/" + data
        server = "https://"+self.host
        url = server + path
        try:
            r = requests.delete(url, headers=self.headers, verify=False)
            status_code = r.status_code
            resp = r.text
            json_response = json.loads(resp)
            print("status code is: " + str(status_code))
            if status_code == 200:
                print "Delete was sucessfull..."
            else:
                r.raise_for_status()
                print "error occured in Delete -->" + resp
            return json_response["id"]
        except requests.exceptions.HTTPError as err:
            print ("Error in connection --> " + str(err))
        finally:
            if r:
                r.close()

    def deletePolicy(self, data):
        """Delete access policy with data given."""
        path = "/api/fmc_config/v1/domain/" + self.uuid + "/policy/accesspolicies/" + data
        server = "https://"+self.host
        url = server + path
        try:
            r = requests.delete(url, headers=self.headers, verify=False)
            status_code = r.status_code
            resp = r.text
            json_response = json.loads(resp)
            print("status code is: " + str(status_code))
            if status_code == 200:
                print "Delete was sucessfull..."
            else:
                r.raise_for_status()
                print "error occured in Delete -->" + resp
            return json_response["id"]
        except requests.exceptions.HTTPError as err:
            print ("Error in connection --> " + str(err))
        finally:
            if r:
                r.close()

    def addDevice(self, data):
        """Create device with data given."""
        path = "/api/fmc_config/v1/domain/" + self.uuid + "/devices/devicerecords"
        server = "https://"+self.host
        url = server + path
        try:
            r = requests.post(url, data=json.dumps(data), headers=self.headers, verify=False)
            status_code = r.status_code
            resp = r.text
            json_response = json.loads(resp)
            print("status code is: " + str(status_code))
            if status_code == 201 or status_code == 202:
                print "Post was sucessfull..."
            else:
                r.raise_for_status()
                print "error occured in POST -->" + resp
        except requests.exceptions.HTTPError as err:
            print ("Error in connection --> " + str(err))
        finally:
            if r:
                r.close()
