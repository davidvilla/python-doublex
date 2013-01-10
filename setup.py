#!/usr/bin/python

import sys
from setuptools import setup, find_packages

# hack to prevent 'test' target exception:
# http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html
import multiprocessing, logging

config = dict(
    name             = 'doublex',
    version          = '1.6',
    description      = 'Test doubles for Python',
    keywords         = ['unit test', 'double', 'stub', 'spy', 'mock'],
    author           = 'David Villa Alises',
    author_email     = 'David.Villa@gmail.com',
    url              = 'https://bitbucket.org/DavidVilla/python-doublex',
    packages         = find_packages(),
    data_files       = [('share/doc/python-doublex', ['README.rst'])],
    test_suite       = 'doublex.test',
    license          = 'GPLv3',
    long_description = open('README.rst').read(),
    classifiers      = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Topic :: Software Development',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
        ])


if sys.version_info >= (3,):
    config.update(
        use_2to3 = True,
        )

setup(**config)
