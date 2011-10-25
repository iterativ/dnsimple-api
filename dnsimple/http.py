# -*- coding: utf-8 -*-
"""
Important note: Kenneth Reitz is awesome!
"""
from dnsimple import __version__
import requests
import simplejson



class SmartRequests(object):
    headers = {
        'user-agent': 'DNSimple Python API (ojii) %s' % __version__
    }
    
    def __init__(self, domain, username, password):
        self.domain = domain
        self.session = requests.session(headers=self.headers, auth=(username, password))
        
    def _url(self, path):
        return '%s%s' % (self.domain, path)

    def request(self, method, path, **kwargs):
        return self.session.request(method, self._url(path), **kwargs)
        
    def get(self, path, **kwargs):
        return self.request('GET', path, **kwargs)
    
    def post(self, path, data, **kwargs):
        return self.request('POST', path, **kwargs)
    
    def put(self, path, data, **kwargs):
        return self.request('PUT', path, **kwargs)
    
    def delete(self, path, **kwargs):
        return self.request('DELETE', path, **kwargs)
    
    def json_get(self, path):
        response = self.get(path, headers={'Accept': 'application/json'})
        if response.status_code == requests.codes.ok:
            return simplejson.loads(response.content)
        else:
            raise RuntimeError('Request failed (%s): Content: %r, Headers: %r' % (response.status_code, response.content, response.headers))
