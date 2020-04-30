import logging
from monetdbe import exceptions
from monetdbe.inter.base import BaseInterAPI

_logger = logging.getLogger(__name__)

try:
    from _monetdbe_cffi import lib, ffi
except ImportError as e:
    _logger.error(e)
    _logger.error("try setting LD_LIBRARY_PATH to point to the location of libembedded.so")
    raise


def check_error(msg):
    if msg:
        _logger.error(msg)
        raise exceptions.DatabaseError(msg)


class CFFIInterAPI(BaseInterAPI):

    def cleanup_result(self, connection, result):
        check_error(lib.monetdb_cleanup_result(connection, result))

    def clear_prepare(self):
        lib.monetdb_clear_prepare()

    def connect(self):
        pconn = ffi.new("monetdb_connection *")
        check_error(lib.monetdb_connect(pconn))
        return pconn[0]

    def disconnect(self, connection):
        check_error(lib.monetdb_disconnect(connection))

    def get_autocommit(self):
        lib.monetdb_get_autocommit()

    def get_columns(self):
        lib.monetdb_get_columns()

    def get_table(self):
        lib.monetdb_get_table()

    def is_initialized(self):
        lib.monetdb_is_initialized()

    def query(self, connection, query: str, make_result: bool = False):
        if make_result:
            p_result = ffi.new("monetdb_result **")
        else:
            p_result = ffi.NULL

        affected_rows = ffi.new("lng *")
        prepare_id = ffi.new("int *")
        check_error(lib.monetdb_query(connection, query.encode(), p_result, affected_rows, prepare_id))

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
        check_error(lib.monetdb_shutdown())

    def startup(self, dbdir=ffi.NULL, sequential: bool = False):
        check_error(lib.monetdb_startup(dbdir, sequential))

    def append(self):
        lib.monetdb_append()
