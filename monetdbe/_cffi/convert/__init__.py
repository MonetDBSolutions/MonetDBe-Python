from typing import List, Optional, Callable, Union, Any, Mapping
from typing import NamedTuple

import numpy as np

from monetdbe._lowlevel import lib, ffi
from monetdbe._cffi.types_ import monetdbe_column, char_p
from monetdbe.converters import converters
from monetdbe.exceptions import ProgrammingError
from monetdbe.pythonize import py_date, py_time, py_timestamp


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
    null_value: Optional[Union[int, float]]


#  monetdb C type, SQL type, numpy type, Cstringtype, pyconverter, null value, comment
type_infos: List[MonetdbTypeInfo] = [
    MonetdbTypeInfo(lib.monetdbe_bool, "boolean", np.dtype(np.bool_), "bool", None, None),
    MonetdbTypeInfo(lib.monetdbe_int8_t, "tinyint", np.dtype(np.int8), "int8_t", None, np.iinfo(np.int8).min),  # type: ignore
    MonetdbTypeInfo(lib.monetdbe_int16_t, "smallint", np.dtype(np.int16), "int16_t", None, np.iinfo(np.int16).min),  # type: ignore
    MonetdbTypeInfo(lib.monetdbe_int32_t, "int", np.dtype(np.int32), "int32_t", None, np.iinfo(np.int32).min),  # type: ignore
    MonetdbTypeInfo(lib.monetdbe_int64_t, "bigint", np.dtype(np.int64), "int64_t", None, np.iinfo(np.int64).min),  # type: ignore
    MonetdbTypeInfo(lib.monetdbe_size_t, None, np.dtype(np.uint64), "size_t", None, None),  # used by monetdb internally
    MonetdbTypeInfo(lib.monetdbe_float, "real", np.dtype(np.float32), "float", py_float, np.finfo(np.float32).min),
    MonetdbTypeInfo(lib.monetdbe_double, "float", np.dtype(np.float64), "double", py_float, np.finfo(np.float64).min),
    MonetdbTypeInfo(lib.monetdbe_str, "string", np.dtype('=O'), "str", make_string, None),
    MonetdbTypeInfo(lib.monetdbe_blob, "blob", np.dtype('=O'), "blob", make_blob, None),
    MonetdbTypeInfo(lib.monetdbe_date, "date", np.dtype('=O'), "date", py_date, None),
    MonetdbTypeInfo(lib.monetdbe_time, "time", np.dtype('=O'), "time", py_time, None),
    MonetdbTypeInfo(lib.monetdbe_timestamp, "timestamp", np.dtype('=O'), "timestamp", py_timestamp, None),
]

numpy_type_map: Mapping[np.dtype, MonetdbTypeInfo] = {i.numpy_type: i for i in type_infos}
monet_c_type_map: Mapping[int, MonetdbTypeInfo] = {i.c_type: i for i in type_infos}


def numpy_monetdb_map(numpy_type: np.dtype):
    if numpy_type.kind in ('i', 'f'):  # type: ignore
        return numpy_type_map[numpy_type]
    raise ProgrammingError("append() only support int and float family types")


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
