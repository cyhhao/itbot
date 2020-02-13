# coding=utf-8
import json

import requests
from requests import Session


class base:
    def __init__(self, headers):
        self.host = 'http://webapps.msxiaobing.com'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        }
        self.headers.update(headers)
        self.session = Session()

    def _request(self, method, url, data):
        url = self.host + url
        if method.lower() == 'get':
            req = self.session.request(method, url, params=data, headers=self.headers)
        else:
            req = self.session.request(method, url, json=data, headers=self.headers)
        return req.text

    def get(self, url, data=None):
        return self._request('get', url, data)

    def post(self, url, data=None):
        return self._request('post', url, data)
