from typing import Any
import datetime
import decimal

from monetdbe.exceptions import InterfaceError


def monet_none(data: type(None)) -> str:
    """
    returns a NULL string
    """
    return "NULL"


def monet_bool(data: bool) -> str:
    """
    returns "true" or "false"
    """
    return ["false", "true"][bool(data)]


def monet_escape(data) -> str:
    """
    returns an escaped string
    """
    data = str(data).replace("\\", "\\\\")
    data = data.replace("\'", "\\\'")
    return f"'{data}'"


def monet_identifier_escape(data) -> str:
    """
    returns an escaped identifier
    """
    data = str(data).replace("\\", "\\\\")
    data = data.replace('"', '\\"')
    return '"%s"' % str(data)


def monet_bytes(data: bytes) -> str:
    """
    converts bytes to string
    """
    return monet_escape(data.decode('utf8'))


def monet_memoryview(data: memoryview) -> str:
    return monet_escape(data.tobytes().decode('utf8'))


mapping = {
    (str, monet_escape),
    (bytes, monet_bytes),
    (memoryview, monet_memoryview),
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
}

mapping_dict = dict(mapping)


def convert(data: Any) -> str:
    """
    Return the appropriate conversion function based upon the python type.
    """
    if type(data) in mapping_dict:
        return mapping_dict[type(data)](data)
    else:
        for type_, func in mapping:
            if issubclass(type(data), type_):
                return func(data)
    raise InterfaceError("type %s not supported as value" % type(data))
