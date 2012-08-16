# -*- coding:utf-8; tab-width:4; mode:python -*-

from .doubles import Stub, Spy, ProxySpy, Mock
from .doubles import method_returning, method_raising
from .doubles import ANY_ARG
from .exc import WrongApiUsage, UnexpectedBehavior
from .matchers import called, called_with, never, meets_expectations
