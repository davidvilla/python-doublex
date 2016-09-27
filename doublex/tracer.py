# -*- coding:utf-8; tab-width:4; mode:python -*-

from .doubles import Stub
from .internal import Method, Property, WrongApiUsage


class MethodTracer(object):
    def __init__(self, logger, method):
        self.logger = logger
        self.method = method

    def __call__(self, *args, **kargs):
        self.logger(str(self.method._create_invocation(args, kargs)))


class PropertyTracer(object):
    def __init__(self, logger, prop):
        self.logger = logger
        self.prop = prop

    def __call__(self, *args, **kargs):
        propname = "%s.%s" % (self.prop.double._classname(), self.prop.key)
        if args:
            self.logger("%s set to %s" % (propname, args[0]))
        else:
            self.logger("%s gotten" % (propname))


class Tracer(object):
    def __init__(self, logger):
        self.logger = logger

    def trace(self, target):
        if isinstance(target, Method):
            self.trace_method(target)
        elif isinstance(target, Stub) or issubclass(target, Stub):
            self.trace_class(target)
        else:
            raise WrongApiUsage('Can not trace %s' % target)

    def trace_method(self, method):
        method.attach(MethodTracer(self.logger, method))

    def trace_class(self, double):
        def attach_new_method(attr):
            if isinstance(attr, Method):
                attr.attach(MethodTracer(self.logger, attr))
            elif isinstance(attr, Property):
                attr.attach(PropertyTracer(self.logger, attr))

        double._new_attr_hooks.append(attach_new_method)
