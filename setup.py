#!/usr/bin/python
# -*- coding:utf-8; tab-width:4; mode:python -*-

import distutils.core

distutils.core.setup(
    name             = 'doublex',
    version          = '0.1',
    author           = 'David Villa',
    author_email     = 'David.Villa@gmail.com',
    packages         = ['doublex'],
    data_files       = [('/usr/share/doc/python-doublex', ['README.rst'])],
    url              = 'https://bitbucket.org/DavidVilla/doublex',
    license          = 'GPLv3',
    description      = 'Test doubles framework for Python',
    long_description = open('README.rst').read(),
)
