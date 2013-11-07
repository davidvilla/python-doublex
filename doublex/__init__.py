# -*- coding:utf-8; tab-width:4; mode:python -*-

from functools import partial

from .doubles import *
from .matchers import *
from .tracer import Tracer
from .internal import WrongApiUsage


def set_default_behavior(double, func):
    double._default_behavior = func
