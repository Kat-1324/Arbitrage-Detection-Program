import requests


class RestClient(object):
    def __init__(self, api_url):
        self.url = api_url.rstrip('/')
        self.session = requests.Session()

    def _send_message(self, method, endpoint, params=None, data=None):
        """Send API request.

        Args:
            method (str): HTTP method (get, post, delete, etc.)
            endpoint (str): Endpoint (to be added to base URL)
            params (Optional[dict]): HTTP request parameters
            data (Optional[str]): JSON-encoded string payload for POST

        Returns:
            dict/list: JSON response

        """
        url = self.url + endpoint
        r = self.session.request(method, url, params=params, data=data, timeout=30)
        return r.json()

    def send_message(self, method, endpoint, params=None, data=None):
        return self._send_message(method, endpoint, params, data)

    def receive_text(self, method, endpoint, params=None, data=None):
        url = self.url + endpoint
        r = self.session.request(method, url, params=params, data=data, timeout=30)
        return r.text

    def get(self, endpoint, params=None, data=None):
        return self._send_message('get', endpoint, params, data)

    def post(self, endpoint, params=None, data=None):
        return self._send_message('post', endpoint, params, data)

    def put(self, endpoint, params=None, data=None):
        return self._send_message('put', endpoint, params, data)

    def delete(self, endpoint, params=None, data=None):
        return self._send_message('delete', endpoint, params, data)
