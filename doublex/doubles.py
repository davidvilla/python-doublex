# -*- coding:utf-8; tab-width:4; mode:python -*-

import inspect

from .internal import ANY_ARG, Method,  get_class
from protos import *


__all__ = ['Stub', 'Spy', 'ProxySpy', 'Mock', 'Mimic',
           'method_returning', 'method_raising',
           'ANY_ARG']



class Stub(object):
    __metaclass__ = DoubleFactory


class Spy(object):
    __metaclass__ = DoubleFactory


class ProxySpy(object):
    __metaclass__ = DoubleFactory


class Mock(object):
    __metaclass__ = DoubleFactory


def Mimic(double_factory, collab):
    def getattribute(self, key):
        if key in ['__class__', '__dict__',
                   '_get_method', '_methods'] or \
                key in [x[0] for x in inspect.getmembers(double)] or \
                key in self.__dict__:
            return object.__getattribute__(self, key)

        return self._get_method(key)

    def _get_method(self, key):
        if key not in self._methods.keys():
            assert self._proxy.get_attr_typeid(key) == 'instancemethod'
            method = Method(self, key)
            self._methods[key] = method

        return self._methods[key]

    double = double_factory.create_class()
    assert issubclass(double, StubProto), \
        "Mimic() takes a double class as first argument (got %s instead)" & double

    collab_class = get_class(collab)
    generated_class = type(
        "Mimic_%s_for_%s" % (double.__name__, collab_class.__name__),
        (double, collab_class) + collab_class.__bases__,
        dict(_methods = {},
             __getattribute__ = getattribute,
             _get_method = _get_method))
    return generated_class(collab)


def method_returning(value):
    with Stub() as stub:
        method = Method(stub, 'unnamed')
        method(ANY_ARG).returns(value)
        return method


def method_raising(exception):
    with Stub() as stub:
        method = Method(stub, 'unnamed')
        method(ANY_ARG).raises(exception)
        return method
