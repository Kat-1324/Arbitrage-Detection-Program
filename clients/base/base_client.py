import requests


class BaseClient(object):
    """ Base client class. """

    def __init__(self, api_url):
        self.url = api_url
        self.session = requests.Session()

    def _send_message(self, method, endpoint, params=None, data=None):
        """Send API request. Returns a dict/list - JSON response """

        url = self.url + endpoint
        r = self.session.request(method, url, params=params, data=data, timeout=30)
        return r.json()

    def send_message(self, method, endpoint, params=None, data=None):
        return self._send_message(method, endpoint, params, data)

    def close(self):
        self.session.close()
