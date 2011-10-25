############
Installation
############

Inside a virtualenv, run ``pip install dnsimple-api``.

#####
Usage
#####

Get started::

    from dnsimple.api import DNSimple
    
    mydns = DNSimple('myusername', 'mypassword')
    
Get a list of your domains::

    mydns.domains
    
Access a single domain::

    example = mydns.domains['example.com']
    
Show records of that domain::

    example.records
    
Add a new record (in this case a subdomain called "test")::

    example.add_record('test', 'A', '1.2.3.4')
