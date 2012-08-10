# -*- coding:utf-8; tab-width:4; mode:python -*-


def inspect_count_positionals(argspec):
    if argspec.defaults is None:
        ndefaults = 0
    else:
        ndefaults = len(argspec.defaults)

    return len(argspec.args) - ndefaults - 1


def inspect_get_keywords(argspec):
    if argspec.defaults is None:
        return []

    return argspec.args[-len(argspec.defaults):]
