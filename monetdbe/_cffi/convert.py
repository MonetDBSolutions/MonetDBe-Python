from typing import List, Tuple, Optional, Callable, Union, Any

import numpy as np
from monetdbe._lowlevel import lib, ffi

from monetdbe.converters import converters
from monetdbe.exceptions import ProgrammingError
from monetdbe.pythonize import py_date, py_time, py_timestamp


def make_string(blob: ffi.CData) -> str:
    if blob:
        return ffi.string(blob).decode()
    else:
        return ""


def make_blob(blob: ffi.CData) -> str:
    if blob:
        return ffi.string(blob.data[0:blob.size])
    else:
        return ""


def py_float(data: ffi.CData) -> float:
    """
    Convert a monetdb FFI float to a python float
    """
    if 'FLOAT' in converters:  # type: ignore
        return converters['FLOAT'](data)
    elif 'DOUBLE' in converters:  # type: ignore
        return converters['DOUBLE'](data)
    else:
        return data


#  monetdb C type, SQL type, numpy type, Cstringtype, pyconverter, null value, comment
mappings: List[Tuple[int, Optional[str], np.dtype, str, Optional[Callable], Optional[Union[int, float]]]] = [
    (lib.monetdbe_bool, "boolean", np.dtype(np.bool_), "bool", None, None),
    (lib.monetdbe_int8_t, "tinyint", np.dtype(np.int8), "int8_t", None, np.iinfo(np.int8).min),  # type: ignore
    (lib.monetdbe_int16_t, "smallint", np.dtype(np.int16), "int16_t", None, np.iinfo(np.int16).min),  # type: ignore
    (lib.monetdbe_int32_t, "int", np.dtype(np.int32), "int32_t", None, np.iinfo(np.int32).min),  # type: ignore
    (lib.monetdbe_int64_t, "bigint", np.dtype(np.int64), "int64_t", None, np.iinfo(np.int64).min),  # type: ignore
    (lib.monetdbe_size_t, None, np.dtype(np.uint64), "size_t", None, None),  # used by monetdb internally
    (lib.monetdbe_float, "real", np.dtype(np.float32), "float", py_float, np.finfo(np.float32).min),
    (lib.monetdbe_double, "float", np.dtype(np.float64), "double", py_float, np.finfo(np.float64).min),
    (lib.monetdbe_str, "string", np.dtype('=O'), "str", make_string, None),
    (lib.monetdbe_blob, "blob", np.dtype('=O'), "blob", make_blob, None),
    (lib.monetdbe_date, "date", np.dtype('=O'), "date", py_date, None),
    (lib.monetdbe_time, "time", np.dtype('=O'), "time", py_time, None),
    (lib.monetdbe_timestamp, "timestamp", np.dtype('=O'), "timestamp", py_timestamp, None),
]
numpy2monet_map = {numpy_type: (c_string, monet_type) for monet_type, _, numpy_type, c_string, _, _ in mappings}
monet_numpy_map = {monet_type: (c_string, converter, numpy_type, null_value) for
                   monet_type, _, numpy_type, c_string, converter, null_value in mappings}


def numpy_monetdb_map(numpy_type: np.dtype):
    if numpy_type.kind in ('i', 'f'):  # type: ignore
        return numpy2monet_map[numpy_type]
    raise ProgrammingError("append() only support int and float family types")


def extract(rcol: ffi.CData, r: int, text_factory: Optional[Callable[[str], Any]] = None):
    """
    Extracts values from a monetdbe_column.

    The text_factory is optional, and wraps the value with a custom user supplied text function.
    """
    cast_string, cast_function, numpy_type, monetdbe_null = monet_numpy_map[rcol.type]
    col = ffi.cast(f"monetdbe_column_{cast_string} *", rcol)
    if col.is_null(col.data + r):
        return None
    else:
        if cast_function:
            result = cast_function(col.data[r])
            if rcol.type == lib.monetdbe_str and text_factory:
                return text_factory(result)
            else:
                return result
        else:
            return col.data[r]
