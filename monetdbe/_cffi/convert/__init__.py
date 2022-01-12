from decimal import Decimal
from typing import List, Optional, Callable, Union, Any, Mapping, NamedTuple
import logging

import numpy as np

from monetdbe._lowlevel import lib, ffi
from monetdbe._cffi.types_ import monetdbe_column, char_p
from monetdbe.converters import converters
from monetdbe.exceptions import ProgrammingError
from monetdbe.pythonize import py_date, py_time, py_timestamp
from monetdbe._cffi.branch import newer_then_jul2021

from monetdbe.types import supported_numpy_types

_logger = logging.getLogger()


def make_string(blob: char_p) -> str:
    if blob:
        return ffi.string(blob).decode()
    else:
        return ""


def make_blob(blob: char_p) -> str:
    if blob:
        return ffi.string(blob.data[0:blob.size])
    else:
        return ""


def py_float(data: char_p) -> float:
    """
    Convert a monetdb FFI float to a python float
    """
    if 'FLOAT' in converters:  # type: ignore
        return converters['FLOAT'](data)
    elif 'DOUBLE' in converters:  # type: ignore
        return converters['DOUBLE'](data)
    else:
        return data


class MonetdbTypeInfo(NamedTuple):
    c_type: int
    sql_type: Optional[str]
    numpy_type: np.dtype
    c_string_type: str
    py_converter: Optional[Callable]


inversable_type_infos: List[MonetdbTypeInfo] = [
    MonetdbTypeInfo(lib.monetdbe_bool, "boolean", np.dtype(np.bool_), "bool", None),
    MonetdbTypeInfo(lib.monetdbe_int8_t, "tinyint", np.dtype(np.int8), "int8_t", None),  # type: ignore
    MonetdbTypeInfo(lib.monetdbe_int16_t, "smallint", np.dtype(np.int16), "int16_t", None),  # type: ignore
    MonetdbTypeInfo(lib.monetdbe_int32_t, "int", np.dtype(np.int32), "int32_t", None),  # type: ignore
    MonetdbTypeInfo(lib.monetdbe_int64_t, "bigint", np.dtype(np.int64), "int64_t", None),  # type: ignore
    MonetdbTypeInfo(lib.monetdbe_float, "real", np.dtype(np.float32), "float", py_float),
    MonetdbTypeInfo(lib.monetdbe_double, "float", np.dtype(np.float64), "double", py_float),
]

# things that can have a mapping from numpy to monetdb but not back
numpy_to_monetdb_type_infos: List[MonetdbTypeInfo] = [
    MonetdbTypeInfo(lib.monetdbe_int8_t, "tinyint", np.dtype(np.uint8), "int8_t", None),
    MonetdbTypeInfo(lib.monetdbe_int16_t, "smallint", np.dtype(np.uint16), "int16_t", None),
    MonetdbTypeInfo(lib.monetdbe_int32_t, "int", np.dtype(np.uint32), "int32_t", None),
    MonetdbTypeInfo(lib.monetdbe_int64_t, "bigint", np.dtype(np.uint64), "int64_t", None),
]

# things that can have a mapping from monetdb to numpy but not back
monetdb_to_numpy_type_infos: List[MonetdbTypeInfo] = [
    MonetdbTypeInfo(lib.monetdbe_str, "string", np.dtype('=O'), "str", make_string),
    MonetdbTypeInfo(lib.monetdbe_blob, "blob", np.dtype('=O'), "blob", make_blob),
    MonetdbTypeInfo(lib.monetdbe_date, "date", np.dtype('=O'), "date", py_date),
    MonetdbTypeInfo(lib.monetdbe_time, "time", np.dtype('=O'), "time", py_time),
    MonetdbTypeInfo(lib.monetdbe_timestamp, "timestamp", np.dtype('=O'), "timestamp", py_timestamp),
]

numpy_type_map: Mapping[np.dtype, MonetdbTypeInfo] = {i.numpy_type: i for i in
                                                      inversable_type_infos + numpy_to_monetdb_type_infos}
monet_c_type_map: Mapping[int, MonetdbTypeInfo] = {i.c_type: i for i in
                                                   inversable_type_infos + monetdb_to_numpy_type_infos}


def precision_warning(from_: int, to: int):
    if from_ == lib.monetdbe_int64_t and to in (lib.monetdbe_int32_t, lib.monetdbe_int16_t, lib.monetdbe_int8_t):
        _logger.warning("appending 64-bit data to lower bit column, potential loss of precision")
    elif from_ == lib.monetdbe_int32_t and to in (lib.monetdbe_int16_t, lib.monetdbe_int8_t):
        _logger.warning("appending 32-bit data to lower bit column, potential loss of precision")
    elif from_ == lib.monetdbe_int16_t and to == lib.monetdbe_int8_t:
        _logger.warning("appending 16-bit data to 8-bit column, potential loss of precision")
    elif from_ in (lib.monetdbe_float, lib.monetdbe_double) and \
            to in (lib.monetdbe_int64_t, lib.monetdbe_int32_t, lib.monetdbe_int16_t, lib.monetdbe_int8_t):
        _logger.warning("appending float values to int column")


def numpy_monetdb_map(numpy_type: np.dtype):
    if numpy_type.kind == 'U':
        # this is an odd one, the numpy type string includes the width. Also, we don't format
        # monetdb string columns as fixed width numpy columns yet, so technically this type is
        # non-reversable for now.
        return MonetdbTypeInfo(lib.monetdbe_str, "string", numpy_type, "char *", None)
    if numpy_type.kind == 'M':
        # TODO: another odd one
        return MonetdbTypeInfo(lib.monetdbe_timestamp, "timestamp", np.dtype(np.datetime64), "int64_t", None)

    if numpy_type.kind in supported_numpy_types:  # type: ignore
        return numpy_type_map[numpy_type]
    raise ProgrammingError(f"append() called with unsupported type {numpy_type}")


def timestamp_to_date():
    return MonetdbTypeInfo(lib.monetdbe_date, "date", np.dtype(np.datetime64), "int64_t", None)


def get_null_value(rcol: monetdbe_column):
    type_info = monet_c_type_map[rcol.type]
    col = ffi.cast(f"monetdbe_column_{type_info.c_string_type} *", rcol)
    return col.null_value


if newer_then_jul2021:
    def extract(rcol: monetdbe_column, r: int, text_factory: Optional[Callable[[str], Any]] = None):
        """
        Extracts values from a monetdbe_column.

        The text_factory is optional, and wraps the value with a custom user supplied text function.
        """

        type_info = monet_c_type_map[rcol.type]
        col = ffi.cast(f"monetdbe_column_{type_info.c_string_type} *", rcol)
        if col.is_null(col.data + r):
            return None
        else:
            col_data = col.data[r]
            if rcol.sql_type.name != ffi.NULL and ffi.string(rcol.sql_type.name).decode() == 'decimal':
                col_data = Decimal(col_data) / (Decimal(10) ** rcol.sql_type.scale)
            if type_info.py_converter:
                result = type_info.py_converter(col_data)
                if rcol.type == lib.monetdbe_str and text_factory:
                    return text_factory(result)
                return result
            return col_data
else:
    def extract(rcol: monetdbe_column, r: int, text_factory: Optional[Callable[[str], Any]] = None):
        """
        Extracts values from a monetdbe_column.
        The text_factory is optional, and wraps the value with a custom user supplied text function.
        """
        type_info = monet_c_type_map[rcol.type]
        col = ffi.cast(f"monetdbe_column_{type_info.c_string_type} *", rcol)
        if col.is_null(col.data + r):
            return None
        else:
            if type_info.py_converter:
                result = type_info.py_converter(col.data[r])
                if rcol.type == lib.monetdbe_str and text_factory:
                    return text_factory(result)
                return result
            return col.data[r]
