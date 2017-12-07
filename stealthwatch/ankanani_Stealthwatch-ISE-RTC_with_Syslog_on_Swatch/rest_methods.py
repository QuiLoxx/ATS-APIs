import json
import requests
requests.packages.urllib3.disable_warnings()

#ISE get requires headers.  AMP does not.  
def iseget(url, headers):
	try:
		response = requests.get(url, headers=headers, verify=False)
		# Consider any status other than 2xx an error
		if not response.status_code // 100 == 2:
			return "Error: Unexpected response {}".format(response)
		try:
			return response.json()
		except:
			return "Error: Non JSON response {}".format(response.text)
	except requests.exceptions.RequestException as e:
		# A serious problem happened, like an SSLError or InvalidURL
		return "Error: {}".format(e)

def iseput(url, headers, data):
	try:
		response = requests.put(url, json.dumps(data), headers=headers, verify=False)
		# Consider any status other than 2xx an error
		if not response.status_code // 100 == 2:
			return "Error: Unexpected response {}".format(response)
		try:
			return response.json()
		except:
			if response.status_code:
				return "Null"
			return "Error: Non JSON response {}".format(response.text)
	except requests.exceptions.RequestException as e:
		# A serious problem happened, like an SSLError or InvalidURL
		return "Error: {}".format(e)
