# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from dnsimple import __version__ as version
import os

README = os.path.join(os.path.dirname(__file__), 'README.rst')

with open(README) as fobj:
    long_description = fobj.read()

setup(
    name="dnsimple-api",
    version=version,
    description="dnsimple.com API wrapper",
    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='dnsimple dns api',
    author='Jonas Obrist',
    author_email='jonas.obrist@djee.se',
    url='http://github.com/ojii/dnsimple-api',
    license='BSD',
    packages=find_packages(),
    install_requires=[
        'simplejson',
        'requests>=0.7.2'
    ],
    include_package_data=True,
    zip_safe=False
)
