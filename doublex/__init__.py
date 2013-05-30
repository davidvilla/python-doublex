# -*- coding:utf-8; tab-width:4; mode:python -*-

from .doubles import *
from .matchers import *
from .internal import WrongApiUsage


def set_default_behavior(double, func):
    double._default_behavior = func


def when(double):
    if not isinstance(double, Stub):
        raise WrongApiUsage("when() takes a double, '%s' given" % double)

    double._activate_next()
    return double


def expect_call(mock):
    if not isinstance(mock, Mock):
        raise WrongApiUsage("expect_call() takes a mock, '%s' given" % mock)

    mock._activate_next()
    return mock
