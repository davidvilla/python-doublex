#!/usr/bin/env python

from distutils.core import setup

setup(name             = 'doublex',
      version          = '1.5',
      description      = 'Test doubles framework for Python',
      author           = 'David Villa Alises',
      author_email     = 'David.Villa@gmail.com',
      url              = 'https://bitbucket.org/DavidVilla/python-doublex',
      packages         = ['doublex'],
      data_files       = [('share/doc/python-doublex', ['README.rst'])],
      license          = 'GPLv3',
      long_description = open('README.rst').read(),
      classifiers      = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
        ],
)
