# -*- coding:utf-8; tab-width:4; mode:python -*-

from .doubles import *
from .matchers import *
from .tracer import Tracer
from .internal import WrongApiUsage


def set_default_behavior(double, func):
    double._default_behavior = func


def when(double):
    if not isinstance(double, Stub):
        raise WrongApiUsage("when() takes a double, '%s' given" % double)

    if isinstance(double, Mock):
        raise WrongApiUsage("when() takes a stub or spy. Use expect_call() for mocks")

    return double._activate_next()


def expect_call(mock):
    if not isinstance(mock, Mock):
        raise WrongApiUsage("expect_call() takes a mock, '%s' given" % mock)

    return mock._activate_next()
