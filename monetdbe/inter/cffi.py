from .base import BaseInterAPI
from cffi import FFI
from pathlib import Path

path = str(Path(__file__).parent / 'embed.h')


class CFFIInterAPI(BaseInterAPI):
    def __init__(self):
        ffibuilder = FFI()
        with open(path, 'r') as f:
            ffibuilder.cdef(f.read())
        ffibuilder.set_source("_monetdbe_cffi", libraries=['embedded'])
        ffibuilder.compile(verbose=True)

    def cleanup_result(self):
        pass

    def clear_prepare(self):
        pass

    def connect(self):
        pass

    def disconnect(self):
        pass

    def get_autocommit(self):
        pass

    def get_columns(self):
        pass

    def get_table(self):
        pass

    def is_initialized(self):
        pass

    def query(self):
        pass

    def result_fetch(self):
        pass

    def result_fetch_rawcol(self):
        pass

    def send_close(self):
        pass

    def set_autocommit(self):
        pass

    def shutdown(self):
        pass

    def startup(self):
        pass

    def append(self):
        pass
