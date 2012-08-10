# -*- coding:utf-8; tab-width:4; mode:python -*-

import types
import inspect

from hamcrest.core.base_matcher import BaseMatcher

import tools
import safeunicode


class Spy(object):
    def __init__(self, collaborator=None):
        self.proxy = create_collaborator_proxy(collaborator)
        self.invocations = []

    def add_invocation(self, invocation):
        self.proxy.assert_match_signature(invocation)
        self.invocations.append(invocation)

    def was_called(self, invocation, times):
        return self.invocations.count(invocation) >= times

    def __getattr__(self, key):
        self.proxy.assert_has_method(key)

        method = Method(self, key)
        setattr(self, key, method)
        return method


def create_collaborator_proxy(collaborator):
    if collaborator is None:
        return DummyCollaboratorProxy()

    return CollaboratorProxy(collaborator)


class DummyCollaboratorProxy(object):
    def assert_has_method(self, name):
        pass

    def assert_match_signature(self, invocation):
        pass


class CollaboratorProxy(object):
    def __init__(self, collaborator):
        self.collaborator = self.get_class(collaborator)

    def get_class(self, something):
        if isinstance(something, (types.ClassType, type)):
            return something

        if isinstance(something, (types.InstanceType, object)):
            return something.__class__

        raise Exception("collaborator must be class or instance")

    def assert_match_signature(self, invocation):
        self.assert_has_method(invocation.name)
        method = getattr(self.collaborator, invocation.name)
        argspec = inspect.getargspec(method)

#        print method.__class__

#        print len(invocation.context.args), len(argspec.args)
#        print "args:", argspec.args
#        print "varargs:", argspec.varargs
#        print "keywords:", argspec.keywords
#        print "defaults:", argspec.defaults

        positionals = tools.inspect_count_positionals(argspec)
        keywords = tools.inspect_get_keywords(argspec)

#        print keywords

        if len(invocation.context.args) != positionals:
            reason = "Mismatching positional arguments:\n%s" %\
                self.add_class_prefix(invocation.name,
                                      inspect.formatargspec(*argspec))
            raise ApiMismatch(reason)

#        print invocation, argspec

    def assert_has_method(self, name):
        if not hasattr(self.collaborator, name):
            reason = "No such method: %s" % self.add_class_prefix(name)
            raise ApiMismatch(reason)

    def add_class_prefix(self, name, args=''):
        return "%s.%s%s" % (self.collaborator.__name__, name, args)


class Method(object):
    def __init__(self, double, name):
        self.double = double
        self.name = name

    def __call__(self, *args, **kargs):
        self.double.add_invocation(
            Invocation(self.name, InvocationContext(*args, **kargs)))

    def was_called(self, context, times):
        return self.double.was_called(
            Invocation(self.name, context), times)

    def __repr__(self):
        return "Method(%s)" % self.name


class Invocation(object):
    def __init__(self, name, context):
        self.name = name
        self.context = context

    def __eq__(self, other):
        return (self.name, self.context) == (other.name, other.context)

    def __repr__(self):
        return "%s%s" % (self.name, self.context)


class InvocationContext(object):
    def __init__(self, *args, **kargs):
        self.args = args
        self.kargs = kargs

    def any_arg(self):
        return ANY_ARG in self.args

    def __eq__(self, other):
        if self.any_arg() or other.any_arg():
            return True

        return (self.args, self.kargs) == (other.args, other.kargs)

    def __str__(self):
        return str(InvocationFormatter(self.args, self.kargs))


class MethodCalled(BaseMatcher):
    def __init__(self, context, times=1):
        self.context = context
        self._times = times

    def _matches(self, method):
        return method.was_called(self.context, self._times)

    def describe_to(self, description):
        description.append_text('method called ')
        if self._times > 1:
            description.append_text('%s times ' % self._times)

    def times(self, n):
        return MethodCalled(self.context, times=n)


def called():
    return MethodCalled(InvocationContext(ANY_ARG))


def called_with(*args, **kargs):
    return MethodCalled(InvocationContext(*args, **kargs))


ANY_ARG = "__ANY_ARG__"


class ApiMismatch(Exception):
    pass


class InvocationFormatter(object):
    def __init__(self, args, kargs):
        self.args = args
        self.kargs = kargs
        self.output = None

    def __str__(self):
        arg_values = []
        if self.args:
            arg_values.append(self._format_args(self.args))
        if self.kargs:
            arg_values.append(self._format_kargs(self.kargs))

        return "(%s) -> %s" % (str.join(', ', arg_values),
                               repr(self.output))

    @staticmethod
    def _format_args(args):
        str_args = []
        for arg in args:
            if isinstance(arg, unicode):
                arg = safeunicode.get_string(arg)

            if isinstance(arg, (int, str, dict)):
                str_args.append(repr(arg))
            else:
                str_args.append(str(arg))

        return str.join(', ', str_args)

    @staticmethod
    def _format_kargs(kargs):
        items = ['%s=%s' % (key, repr(val))
                 for key, val in sorted(kargs.items())]

        return str.join(', ', items)
