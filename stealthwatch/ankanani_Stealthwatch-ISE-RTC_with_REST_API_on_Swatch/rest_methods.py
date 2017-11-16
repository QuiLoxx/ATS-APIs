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

def ampget(url):
	try:
		response = requests.get(url)
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

def smcget(url, headers):
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

def smcauth(SMC_hostname, SMC_username, SMC_password):
	try:
		url = "https://{}/token/v2/authenticate".format(SMC_hostname)
		smcheaders = {
			"Content-Type": "application/x-www-form-urlencoded",
		}
		data = "username="+SMC_username+"&password="+SMC_password
		response = requests.post(url, data, headers=smcheaders, verify=False)
		# Consider any status other than 2xx an error
		if not response.status_code // 100 == 2:
			return "Error: Unexpected response {}".format(response)
		try:
			return response.headers['Set-Cookie'][:]
		except:
			return "Error: Non JSON response {}".format(response.text)
	except requests.exceptions.RequestException as e:
		# A serious problem happened, like an SSLError or InvalidURL
		return "Error: {}".format(e)

def smcpost(url, headers, data):
	try:
		response = requests.post(url, json.dumps(data), headers=headers, verify=False)
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

def amppatch(url, headers, data):
	try:
		response = requests.patch(url, json.dumps(data), headers=headers, verify=True)
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
