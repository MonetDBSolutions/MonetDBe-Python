import logging
from pathlib import Path
from typing import Optional, Any, Dict, Tuple, Callable

from monetdbe.pythonize import py_bytes, py_date, py_time, py_timestamp
from monetdbe import exceptions

_logger = logging.getLogger(__name__)

try:
    from _monetdbe_cffi import lib, ffi
except ImportError as e:
    _logger.error(e)
    _logger.error("try setting LD_LIBRARY_PATH to point to the location of libembedded.so")
    raise


def make_string(blob):
    if blob:
        return ffi.string(blob).decode()
    else:
        return ""


def check_error(msg):
    if msg:
        decoded = ffi.string(msg).decode()
        _logger.error(decoded)
        raise exceptions.DatabaseError(decoded)


type_map: Dict[Any, Tuple[str, Optional[Callable]]] = {
    lib.monetdb_int32_t: ("int32_t", None),
    lib.monetdb_str: ("str", make_string),
    lib.monetdb_int8_t: ("int8_t", None),
    lib.monetdb_int16_t: ("int16_t", None),
    lib.monetdb_int64_t: ("int64_t", None),
    lib.monetdb_size_t: ("size_t", None),
    lib.monetdb_float: ("float", None),
    lib.monetdb_double: ("double", None),
    lib.monetdb_blob: ("blob", py_bytes),
    lib.monetdb_date: ("date", py_date),
    lib.monetdb_time: ("time", py_time),
    lib.monetdb_timestamp: ("timestamp", py_timestamp),

}


def extract(rcol, r: int, text_factory: Optional[Callable[[str], Any]] = None):
    """
    Extracts values from a monetdb_column.

    The text_factory is optional, and wraps the value with a custom user supplied text function.
    """
    cast_string, cast_function = type_map[rcol.type]
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
_connection = ffi.NULL


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

    def cleanup_result(self, result):
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

    def result_fetch(self, result, c: int):
        p_rcol = ffi.new("monetdb_column **")
        check_error(lib.monetdb_result_fetch(_connection, p_rcol, result, c))
        return p_rcol[0]

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

    def append(self):
        raise NotImplemented
        # lib.monetdb_append()

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
