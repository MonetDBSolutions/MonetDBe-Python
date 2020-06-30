import datetime
import decimal
from typing import Any, Dict, Type, Callable, Tuple, List

import numpy

from monetdbe.exceptions import InterfaceError


def monet_none(data: None) -> str:
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
    return "'%s'" % data.hex()


def monet_memoryview(data: memoryview) -> str:
    return "'%s'" % data.tobytes().hex()


def monet_float(data: float) -> str:
    if data != data:  # yes this is how you can check if a float is a NaN
        return 'NULL'
    else:
        return str(data)


mapping: List[Tuple[Type, Callable]] = [
    (str, monet_escape),
    (bytes, monet_bytes),
    (memoryview, monet_memoryview),
    (int, str),
    (complex, str),
    (float, monet_float),
    (decimal.Decimal, str),
    (datetime.datetime, monet_escape),
    (datetime.time, monet_escape),
    (datetime.date, monet_escape),
    (datetime.timedelta, monet_escape),
    (bool, monet_bool),
    (type(None), monet_none),
    (numpy.int64, int),
    (numpy.ma.core.MaskedConstant, monet_none),
]

mapping_dict: Dict[Type, Callable] = dict(mapping)


class PrepareProtocol:
    """
    SQLite has a PrepareProtocol class that is passed to a values __conform__ method if it exists.

    This is not well documented, and the __conform__ method seems rejected in PEP 246. Still, the SQLite
    documentation mentions this
    """
    ...


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

    if hasattr(data, '__conform__'):
        try:
            return data.__conform__(PrepareProtocol)
        except Exception as e:
            raise InterfaceError(e)

    raise InterfaceError("type %s not supported as value" % type(data))
