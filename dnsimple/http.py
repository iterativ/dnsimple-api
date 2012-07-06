# -*- coding: utf-8 -*-
"""
Important note: Kenneth Reitz is awesome!
"""
from dnsimple import __version__
import requests
import json


class SmartRequests(object):

    def __init__(self, domain, email, api_token):
        self.domain = domain
        self.email = email
        self.api_token = api_token
        self.session = requests.session(headers=self._create_headers())

    def _create_headers(self):
        headers = {
            'user-agent': 'DNSimple Python API (iterativ) %s' % __version__,
            'accept': 'application/json',
            'X-DNSimple-Token': '%s:%s' % (self.email, self.api_token),
        }
        return headers

    def _url(self, path):
        return '%s%s' % (self.domain, path)

    def request(self, method, path, **kwargs):
        return self.session.request(method, self._url(path), **kwargs)

    def get(self, path, **kwargs):
        return self.request('GET', path, allow_redirects=True, **kwargs)
    
    def post(self, path, data, **kwargs):
        return self.request('POST', path, data=data, allow_redirects=True, **kwargs)
    
    def put(self, path, data, **kwargs):
        return self.request('PUT', path, data=data, allow_redirects=True, **kwargs)
    
    def delete(self, path, **kwargs):
        return self.request('DELETE', path, allow_redirects=True, **kwargs)
    
    def json_get(self, path):
        response = self.get(path)
        if response.ok:
            return json.loads(response.content)
        else:
            raise RuntimeError('Request failed (%s): Content: %r, Headers: %r' % (response.status_code, response.content, response.headers))
