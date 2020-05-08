"""
This file is here for monetdblite backwards compatiblity
"""
import datetime
import decimal
from monetdbe.exceptions import ProgrammingError


def utf8_encode(instr):
    if instr is None:
        return None
    if isinstance(instr, str):
        return instr.encode('utf-8')
    return instr


def monet_none(data):
    """
    returns a NULL string
    """
    return "NULL"


def monet_bool(data):
    """
    returns "true" or "false"
    """
    return ["false", "true"][bool(data)]


def monet_escape(data):
    """
    returns an escaped string
    """
    data = str(data).replace("\\", "\\\\")
    data = data.replace("\'", "\\\'")
    return "'%s'" % str(data)


def monet_identifier_escape(data):
    """
    returns an escaped identifier
    """
    data = str(data).replace("\\", "\\\\")
    data = data.replace('"', '\\"')
    return '"%s"' % str(data)


def monet_bytes(data):
    """
    converts bytes to string
    """
    return monet_escape(data.decode('utf8'))


def monet_unicode(data):
    return monet_escape(data.encode('utf-8'))


mapping = [
    (str, monet_escape),
    (bytes, monet_bytes),
    (int, str),
    (complex, str),
    (float, str),
    (decimal.Decimal, str),
    (datetime.datetime, monet_escape),
    (datetime.time, monet_escape),
    (datetime.date, monet_escape),
    (datetime.timedelta, monet_escape),
    (bool, monet_bool),
    (type(None), monet_none),
]

mapping_dict = dict(mapping)


def convert(data):
    """
    Return the appropriate conversion function based upon the python type.
    """
    if type(data) in mapping_dict:
        return mapping_dict[type(data)](data)
    else:
        for type_, func in mapping:
            if issubclass(type(data), type_):
                return func(data)
    raise ProgrammingError("type %s not supported as value" % type(data))
