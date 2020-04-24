from .base import BaseInterAPI
from _monetdbe_cffi import lib, ffi


class CFFIInterAPI(BaseInterAPI):

    def cleanup_result(self):
        lib.monetdb_cleanup_result()

    def clear_prepare(self):
        lib.monetdb_clear_prepare()

    def connect(self):
        lib.monetdb_connect()

    def disconnect(self):
        lib.monetdb_disconnect()

    def get_autocommit(self):
        lib.monetdb_get_autocommit()

    def get_columns(self):
        lib.monetdb_get_columns()

    def get_table(self):
        lib.monetdb_get_table()

    def is_initialized(self):
        lib.monetdb_is_initialized()

    def query(self):
        lib.monetdb_query()

    def result_fetch(self):
        lib.monetdb_result_fetch()

    def result_fetch_rawcol(self):
        lib.monetdb_result_fetch_rawcol()

    def send_close(self):
        lib.monetdb_send_close()

    def set_autocommit(self):
        lib.monetdb_set_autocommit()

    def shutdown(self):
        lib.monetdb_shutdown()

    def startup(self):
        err = lib.monetdb_startup(ffi.NULL, 0)
        err

    def append(self):
        lib.monetdb_append()
