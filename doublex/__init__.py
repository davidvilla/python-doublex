# -*- coding:utf-8; tab-width:4; mode:python -*-

from .doubles import *
from .matchers import *
from .internal import WrongApiUsage


def set_default_behavior(double, func):
    double._default_behavior = func


def when(double):
    double._setting_up = True
    double._one_shot = True
    return double


def expect_call(mock):
    if not isinstance(mock, Mock):
        raise WrongApiUsage("expect_call() takes a mock, '%s' given" % mock)

    mock._setting_up = True
    mock._one_shot = True
    return mock
