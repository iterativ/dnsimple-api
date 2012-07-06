# -*- coding: utf-8 -*-
"""
Client for DNSimple REST API
https://dnsimple.com/documentation/api
"""
from dnsimple.http import SmartRequests
from dnsimple.utils import simple_cached_property, uncache
import logging
import re
import os
import json


class Record(object):
    def __init__(self, domain, data):
        self.dnsimple = domain.dnsimple
        self.domain = domain
        for key, value in data.items():
            setattr(self, key, value)

    def __repr__(self):
        return u'<Record:%s (%s:%s)>' % (self.name, self.record_type, self.content)

    def update(self, name=None, content=None, ttl=None, prio=None):
        data = {}
        if name:
            data['record[name]'] = name
        if content:
            data['record[content]'] = content
        if ttl:
            data['record[ttl]'] = ttl
        if prio:
            data['record[prio]'] = prio
        if data:
            return self.dnsimple.requests.put('/domains/%s/records/%s' % (self.domain.id, self.id), data).ok
        else:
            logging.warning('Record not updated, no data provided')
            return None

    def delete(self):
        return self.dnsimple.requests.delete('/domains/%s/records/%s' % (self.domain.id, self.id))


class Domain(object):
    def __init__(self, dnsimple, data):
        self.dnsimple = dnsimple
        for key, value in data.items():
            setattr(self, key, value)

    def __repr__(self):
        return u'<Domain: %s>' % self.name

    def add_record(self, name, recordtype, content, ttl=3600, prio=10):
        data = {
            'record[name]': name,
            'record[record_type]': recordtype,
            'record[content]': content,
            'record[ttl]': ttl,
            'record[prio]': prio,
        }
        response = self.dnsimple.requests.post('/domains/%s/records' % self.name, data)
        if response.status_code == 201:
            uncache(self, 'records')
            # print(response.content)
            return True
        else:
            logger.warn(response.content)
            return False

    @simple_cached_property
    def records(self):
        records = self.dnsimple.requests.json_get('/domains/%s/records' % self.id)
        return dict([(data['record']['id'], Record(self, data['record'])) for data in records])

    def delete(self):
        return self.dnsimple.requests.delete('/domains/%s.json' % self.id)

    def apply_google_mail_template(self):
        """googlemx is a standard template defined by DNSimple"""
        result = self.add_record('mail', 'CNAME', 'ghs.googlehosted.com')
        if result:
            return self.apply_template('googlemx')
        return False

    def apply_template(self, template_short_name):
        response = self.dnsimple.requests.post('/domains/%s/templates/%s/apply' % (self.id, template_short_name), {})
        if response.ok:
            uncache(self, 'records')
            return True
        else:
            return False

    def get_record_by_name_and_type(self, name, type):
        for key in self.records:
            record = self.records[key]
            if record.name == name and record.record_type == type:
                return record
        return None

def try_open_file(filepath):
    try:
        with open(filepath) as f:
            return f.read()
    except IOError as e:
        # file does not exists
        return None

class DNSimple(object):
    domain = 'https://dnsimple.com'

    def __init__(self, email, api_token):
        self.requests = SmartRequests(self.domain, email, api_token)

    @classmethod
    def with_auth_file(cls):
        passwordfile = try_open_file(".dnsimple")
        if not passwordfile:
            passwordfile = try_open_file(os.path.expanduser("~/.dnsimple"))
        if not passwordfile:
            logging.warning("""Could not open .dnsimple file - please provide a file .dnsimple in the current directory or in
                the home directory with the content:
                email: <dnsimple_email>
                api_token: <dnsimple API token>""")
            return

        email = re.findall(r'email:.*', passwordfile)[0].split(':')[1].strip()
        api_token = re.findall(r'api_token:.*', passwordfile)[0].split(':')[1].strip()
        return cls(email, api_token)

    @simple_cached_property
    def domains(self):
        """
        Get a list of all domains in your account.
        """
        return dict([(data['domain']['name'], Domain(self, data['domain'])) for data in self.requests.json_get('/domains.json')])

    def create_domain(self, name):
        data = {
            'domain[name]': name
        }
        response = self.requests.post('/domains', data)
        if response.status_code == 201:
            uncache(self, 'domains')
            return True
        else:
            logger.warn(response.content)
            return False

    def checkdomain(self, name):
        return self.requests.json_get('/domains/%s/check' % name)

    def get(self, path):
        return self.requests.json_get(path)

    def post(self, path, data):
        response = self.request.post(path, data)
        return json.loads(response.content)

    def put(self, path, data):
        response = self.request.post(path, data)
        return json.loads(response.content)

    def delete(self, path):
        response = self.requests.delete(path)
        return json.loads(response.content)

    def create_standard_domain(self, name, ip_address):
        """creates a new domain and adds 'www' and 'stage' subdomain and applies the
           Google-Mail template which setups the google mail"""
        result = self.create_domain(name)
        if not result:
            return False
        domain = self.domains.get(name)
        if not domain:
            return False
        if not domain.add_record('', 'A', ip_address):
            return False
        if not domain.add_record('www', 'CNAME', name):
            return False
        if not domain.add_record('stage', 'CNAME', name):
            return False
        return domain.apply_google_mail_template()

    def create_cname_subdomain(self, domain_name, sub_domain_name):
        domain = self.domains.get(domain_name)
        if not domain:
            logger.warn("Domain with name '%s' is unknown", domain_name)
            return False
        return domain.add_record(sub_domain_name, 'CNAME', domain_name)

    def migrate_domain_arecord_to_new_address(self, domain_name, new_ip_address):
        domain = self.domains.get(domain_name)
        if not domain:
            logger.warn("Domain with name '%s' is unknown", domain_name)
            return False
        record = domain.get_record_by_name_and_type('', 'A')
        if not record:
            logger.warn("A-Record with no name not defined")
        return record.update(content=new_ip_address)
