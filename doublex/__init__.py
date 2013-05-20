# -*- coding:utf-8; tab-width:4; mode:python -*-

from .doubles import *
from .matchers import *
from .internal import WrongApiUsage


def set_default_behavior(double, func):
    double._default_behavior = func


def disable_context_setup(double):
    double._doublex_disable_context_setup = True