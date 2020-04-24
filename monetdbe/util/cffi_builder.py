"""
This is a build-time utility that will generate the _monetdbe_cffi
CFFI bridging shared library.
"""
from cffi import FFI
from pathlib import Path

ffibuilder = FFI()

path = str(Path(__file__).parent / 'embed.h')

with open(path, 'r') as f:
    ffibuilder.cdef(f.read())

ffibuilder.set_source("_monetdbe_cffi",
                      """
#include "monetdb/monetdb_embedded.h"
                      """,
                      libraries=['embedded'])

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
