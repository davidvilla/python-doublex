# -*- coding: utf-8 -*-

import sys


def __if_number_get_string(number):
    converted_str = number
    if isinstance(number, (int, float)):
        converted_str = str(number)
    return converted_str


def get_unicode(strOrUnicode, encoding='utf-8'):
    strOrUnicode = __if_number_get_string(strOrUnicode)
    if isinstance(strOrUnicode, unicode):
        return strOrUnicode
    return unicode(strOrUnicode, encoding, errors='ignore')


def get_string(strOrUnicode, encoding='utf-8'):
    strOrUnicode = __if_number_get_string(strOrUnicode)
    if sys.version_info >= (3,):
        return strOrUnicode

    if isinstance(strOrUnicode, unicode):
        return strOrUnicode.encode(encoding)
    return strOrUnicode
