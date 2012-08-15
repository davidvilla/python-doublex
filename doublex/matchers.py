# -*- coding:utf-8; tab-width:4; mode:python -*-

import internal


def called():
    return internal.MethodCalled(internal.InvocationContext(internal.ANY_ARG))


def called_with(*args, **kargs):
    return internal.MethodCalled(internal.InvocationContext(*args, **kargs))


def meets_expectations():
    return internal.MockMeetsExpectations()
