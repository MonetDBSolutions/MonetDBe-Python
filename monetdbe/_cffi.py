from pathlib import Path
from typing import Optional, Any

import logging
from monetdbe import exceptions

_logger = logging.getLogger(__name__)

try:
    from _monetdbe_cffi import lib, ffi
except ImportError as e:
    _logger.error(e)
    _logger.error("try setting LD_LIBRARY_PATH to point to the location of libembedded.so")
    raise


def check_error(msg):
    if msg:
        decoded = ffi.string(msg).decode()
        _logger.error(decoded)
        raise exceptions.DatabaseError(decoded)


class MonetEmbedded:
    connection = ffi.NULL

    def __init__(self, dbdir: Optional[Path] = None):
        self.startup(dbdir)
        self.connection = self.connect()

    def __del__(self):
        self.disconnect()
        self.shutdown()

    def startup(self, dbdir: Optional[Path] = None, sequential: bool = False):
        if not dbdir:
            dbdir = ffi.NULL
        check_error(lib.monetdb_startup(dbdir, sequential))

    def cleanup_result(self, result):
        _logger.info("cleanup_result called")
        if result:
            check_error(lib.monetdb_cleanup_result(self.connection, result))

    def clear_prepare(self):
        lib.monetdb_clear_prepare()

    def connect(self):
        _logger.info("connect called")
        pconn = ffi.new("monetdb_connection *")
        check_error(lib.monetdb_connect(pconn))
        return pconn[0]

    def disconnect(self):
        _logger.info("disconnect called")
        if self.connection != ffi.NULL:
            check_error(lib.monetdb_disconnect(self.connection))
        self.connection = ffi.NULL

    def query(self, query: str, make_result: bool = False) -> (Optional[Any], int, int):
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
        check_error(lib.monetdb_query(self.connection, query.encode(), p_result, affected_rows, prepare_id))

        if make_result:
            result = p_result[0]
        else:
            result = None

        return result, affected_rows[0], prepare_id[0]

    def result_fetch(self):
        lib.monetdb_result_fetch()

    def result_fetch_rawcol(self):
        lib.monetdb_result_fetch_rawcol()

    def send_close(self):
        lib.monetdb_send_close()

    def set_autocommit(self):
        lib.monetdb_set_autocommit()

    def shutdown(self):
        _logger.info("shutdown called")
        check_error(lib.monetdb_shutdown())

    def append(self):
        lib.monetdb_append()

    def get_autocommit(self):
        lib.monetdb_get_autocommit()

    def get_columns(self):
        lib.monetdb_get_columns()

    def get_table(self):
        lib.monetdb_get_table()

    def is_initialized(self):
        lib.monetdb_is_initialized()
