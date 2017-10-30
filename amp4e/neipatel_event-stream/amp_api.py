import requests
import json


class amp (object):
    """Class to define the AMP for endpoints console.

    Attributes
    Endpoint: amp api endpoint
    id: client ID for amp
    key: api key for amp

    """

    def __init__(self, endpoint, client_id, key):
        """Return AMP Object whose attributes are endpoint, id and key."""
        self.endpoint = endpoint
        self.client_id = client_id
        self.key = key
        self.headers = {
            'content-type': 'application/json',
            'accept': 'application/json'
            }

    def get(self, url):
        """GET method for amp."""
        try:
            response = requests.get(
                "https://{}{}".format(self.endpoint, url),
                auth=(self.client_id, self.key),
                headers=self.headers
            )
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

    def post(self, url, data):
        """POST method for amp."""
        try:
            response = requests.post(
                "https://{}{}".format(self.endpoint, url),
                data=json.dumps(data),
                auth=(self.client_id, self.key),
                headers=self.headers
            )
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

    def patch(self, url, data):
        """PATCH method for amp."""
        try:
            response = requests.patch(
                "https://{}{}".format(self.endpoint, url),
                data=json.dumps(data),
                auth=(self.client_id, self.key),
                headers=self.headers
            )
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

    def delete(self, url):
        """DEL method for amp."""
        try:
            response = requests.delete(
                "https://{}{}".format(self.endpoint, url),
                auth=(self.client_id, self.key),
                headers=self.headers
                )
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
