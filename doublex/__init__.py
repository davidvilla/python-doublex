# -*- coding:utf-8; tab-width:4; mode:python -*-

from hamcrest.core.base_matcher import BaseMatcher


class Spy(object):
    def __init__(self, collaborator=None):
        self.collaborator = collaborator

    def assert_collaborator_iface(self, key):
        if self.collaborator is not None and not hasattr(self.collaborator, key):
            raise ApiMismatch()

    def __getattr__(self, key):
        self.assert_collaborator_iface(key)

        method = Method(key)
        setattr(self, key, method)
        return method


class Method(object):
    def __init__(self, name):
        self.name = name
        self.invocations = []

    def __call__(self, *args, **kargs):
        self.invocations.append(Invocation(*args, **kargs))

    def __repr__(self):
        return "Method(%s)" % self.name


class Invocation(object):
    def __init__(self, *args, **kargs):
        self.args = args
        self.kargs = kargs

    def any_arg(self):
        return ANY_ARG in self.args

    def __eq__(self, other):
        if self.any_arg() or other.any_arg():
            return True

        return self.args == other.args and self.kargs == other.kargs

    def __repr__(self):
        return "Invocation(%s, %s)" % (self.args, self.kargs)


class MethodCalled(BaseMatcher):
    def __init__(self, invocation, times=1):
        self.invocation = invocation
        self._times = times

    def _matches(self, method):
        return method.invocations.count(self.invocation) >= self._times

    def describe_to(self, description):
        description.append_text('method called ')
        if self._times > 1:
            description.append_text('%s times ' % self._times)

    def times(self, n):
        return MethodCalled(self.invocation, times=n)


def called():
    return MethodCalled(Invocation(ANY_ARG))


def called_with(*args, **kargs):
    return MethodCalled(Invocation(*args, **kargs))


ANY_ARG = "__ANY_ARG__"


class ApiMismatch(Exception):
    pass
