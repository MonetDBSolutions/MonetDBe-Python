import logging
from pathlib import Path
from typing import Optional, Any, Dict, Tuple, Callable, Type
import numpy as np
from monetdbe.pythonize import py_date, py_time, py_timestamp
from monetdbe import exceptions
from monetdbe.converters import converters

_logger = logging.getLogger(__name__)

try:
    from monetdbe._lowlevel import lib, ffi
except ImportError as e:
    _logger.error(e)
    _logger.error("try setting LD_LIBRARY_PATH to point to the location of libembedded.so")
    raise

def make_string(blob):
    if blob:
        return ffi.string(blob).decode()
    else:
        return ""


def make_blob(blob):
    if blob:
        return ffi.string(blob.data[0:blob.size])
    else:
        return ""

def py_float(data: ffi.CData):
    if 'FLOAT' in converters:
        return converters['FLOAT'](data)
    elif 'DOUBLE' in converters:
        return converters['DOUBLE'](data)
    else:
        return data



def check_error(msg):
    if msg:
        decoded = ffi.string(msg).decode()
        _logger.error(decoded)
        raise exceptions.DatabaseError(decoded)


type_map: Dict[Any, Tuple[str, Optional[Callable], Type]] = {
    lib.monetdb_bool: ("bool", bool, np.dtype(np.bool)),
    lib.monetdb_int8_t: ("int8_t", None, np.dtype(np.int8)),
    lib.monetdb_int16_t: ("int16_t", None, np.dtype(np.int16)),
    lib.monetdb_int32_t: ("int32_t", None, np.dtype(np.int32)),
    lib.monetdb_int64_t: ("int64_t", None, np.dtype(np.int64)),
    lib.monetdb_int128_t: ("int128_t", None, None),
    lib.monetdb_size_t: ("size_t", None, None),
    lib.monetdb_float: ("float", py_float, np.dtype(np.float)),
    lib.monetdb_double: ("double", py_float, np.dtype(np.float)),
    lib.monetdb_str: ("str", make_string, np.dtype(np.str)),
    lib.monetdb_blob: ("blob", make_blob, None),
    lib.monetdb_date: ("date", py_date, np.dtype(np.datetime64)),
    lib.monetdb_time: ("time", py_time, np.dtype(np.datetime64)),
    lib.monetdb_timestamp: ("timestamp", py_timestamp, np.dtype(np.datetime64)),
}


def extract(rcol, r: int, text_factory: Optional[Callable[[str], Any]] = None):
    """
    Extracts values from a monetdb_column.

    The text_factory is optional, and wraps the value with a custom user supplied text function.
    """
    cast_string, cast_function, numpy_type = type_map[rcol.type]
    col = ffi.cast(f"monetdb_column_{cast_string} *", rcol)
    if col.is_null(col.data[r]):
        return None
    else:
        if cast_function:
            result = cast_function(col.data[r])
            if rcol.type == lib.monetdb_str and text_factory:
                return text_factory(result)
            else:
                return result
        else:
            return col.data[r]


# Todo: hack to get around the single embed instance limitation
_conn_params = {}
_active = None
_connection: ffi.CData = ffi.NULL


class MonetEmbedded:
    def __init__(self, dbdir: Optional[Path] = None):
        _conn_params[self] = dbdir
        self._switch()

    def __del__(self):
        global _conn_params, _active
        if _active:
            self.disconnect()
            self.shutdown()
        _conn_params.pop(self)
        _active = None

    def _switch(self):
        global _active, _conn_params
        if _active == self:
            return
        global _connection
        if _connection:
            self.disconnect()
            self.shutdown()
        dbdir = _conn_params[self]
        self.startup(dbdir)
        _connection = self.connect()
        self._active = self

    def startup(self, dbdir: Optional[Path] = None, sequential: bool = False):
        if not dbdir:
            dbdir_c = ffi.NULL
        else:
            dbdir_c = ffi.new("char[]", str(dbdir).encode())
        check_error(lib.monetdb_startup(dbdir_c, sequential))

    def shutdown(self):
        _logger.info("shutdown called")
        check_error(lib.monetdb_shutdown())

    def cleanup_result(self, result: ffi.CData):
        _logger.info("cleanup_result called")
        if result:
            check_error(lib.monetdb_cleanup_result(_connection, result))

    def connect(self):
        _logger.info("connect called")
        pconn = ffi.new("monetdb_connection *")
        check_error(lib.monetdb_connect(pconn))
        return pconn[0]

    def disconnect(self):
        _logger.info("disconnect called")
        global _connection
        if _connection != ffi.NULL:
            check_error(lib.monetdb_disconnect(_connection))
        _connection = ffi.NULL

    def query(self, query: str, make_result: bool = False) -> Tuple[Optional[Any], int, int]:
        """
        Execute a query.

        query: the query
        make_results: Create and return a result object. If enabled, you need to call cleanup_result on the
                      result afterwards

        returns:
            result, affected_rows, prepare_id

        """
        if make_result:
            p_result = ffi.new("monetdb_result **")
        else:
            p_result = ffi.NULL

        affected_rows = ffi.new("lng *")
        prepare_id = ffi.new("int *")
        check_error(lib.monetdb_query(_connection, query.encode(), p_result, affected_rows, prepare_id))

        if make_result:
            result = p_result[0]
        else:
            result = None

        return result, affected_rows[0], prepare_id[0]

    def result_fetch(self, result: ffi.CData, column: int):
        p_rcol = ffi.new("monetdb_column **")
        check_error(lib.monetdb_result_fetch(_connection, result, p_rcol, column))
        return p_rcol[0]

    def result_fetch_numpy(self, monetdb_result: ffi.CData):

        result = {}
        for c in range(monetdb_result.ncols):
            p_rcol = ffi.new("monetdb_column **")
            check_error(lib.monetdb_result_fetch(_connection, monetdb_result, p_rcol, c))
            rcol = p_rcol[0]
            name = make_string(rcol.name)
            cast_string, cast_function, numpy_type = type_map[rcol.type]
            buffer_size = monetdb_result.nrows * numpy_type.itemsize
            c_buffer = ffi.buffer(rcol.data, buffer_size)
            np_col = np.frombuffer(c_buffer, dtype=numpy_type)
            result[name] = np_col
        return result

    def clear_prepare(self):
        raise NotImplemented
        # lib.monetdb_clear_prepare()

    def result_fetch_rawcol(self):
        raise NotImplemented
        # lib.monetdb_result_fetch_rawcol()

    def send_close(self):
        raise NotImplemented
        # lib.monetdb_send_close()

    def set_autocommit(self):
        raise NotImplemented
        # lib.monetdb_set_autocommit()

    def append(self, schema: str, table: str, batids, column_count: int):
        check_error(lib.monetdb_append(_connection, schema.encode(), table.encode(), batids, column_count))

    def get_autocommit(self):
        raise NotImplemented
        # lib.monetdb_get_autocommit()

    def get_columns(self):
        raise NotImplemented
        # lib.monetdb_get_columns()

    def get_table(self):
        raise NotImplemented
        # lib.monetdb_get_table()

    def is_initialized(self):
        raise NotImplemented
        # lib.monetdb_is_initialized()
