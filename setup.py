#!/usr/bin/env python

# Copyright (C) 2012-2018 David Villa Alises
#
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import sys
from setuptools import setup, find_packages

# hack to prevent 'test' target exception:
# http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html
import multiprocessing, logging


exec(open('version.py').read())


def local_open(fname):
    return open(os.path.join(os.path.dirname(__file__), fname))


exec(local_open('version.py').read())

config = dict(
    name             = 'doublex',
    version          = __version__,
    description      = 'Python test doubles',
    keywords         = ['unit tests', 'doubles', 'stub', 'spy', 'mock'],
    author           = 'David Villa Alises,  David Pärsson',
    author_email     = 'David.Villa@gmail.com, david@parsson.se',
    url              = 'https://github.com/DavidVilla/python-doublex',
    packages         = ['doublex'],
    data_files       = [('', ['README.rst'])],
    test_suite       = 'doublex.test',
    license          = 'GPLv3',
    long_description = local_open('README.rst').read(),
    install_requires = local_open('requirements.txt').readlines(),
    python_requires  = '>=3.6',
    classifiers      = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
        ],
    )

setup(**config)
