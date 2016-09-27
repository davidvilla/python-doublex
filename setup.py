#!/usr/bin/python

import os
import sys
from setuptools import setup, find_packages

# hack to prevent 'test' target exception:
# http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html
import multiprocessing, logging


def local_open(fname):
    return open(os.path.join(os.path.dirname(__file__), fname))


exec(local_open('version.py').read())


config = dict(
    name             = 'doublex',
    version          = __version__,
    description      = 'Python test doubles',
    keywords         = ['unit tests', 'doubles', 'stub', 'spy', 'mock'],
    author           = 'David Villa Alises',
    author_email     = 'David.Villa@gmail.com',
    url              = 'https://bitbucket.org/DavidVilla/python-doublex',
    packages         = find_packages(),
    data_files       = [('', ['README.rst'])],
    test_suite       = 'doublex.test',
    license          = 'GPLv3',
    long_description = local_open('README.rst').read(),
    install_requires = local_open('requirements.txt').readlines(),
    classifiers      = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
        ],
    )

if sys.version_info >= (3,):
    config.update(dict(
        use_2to3 = True,
        test_suite = 'doublex.test3',
    ))

setup(**config)
