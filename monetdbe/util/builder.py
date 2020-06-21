"""
This is a build-time utility that will generate the monetdbe._lowlevel
CFFI bridging shared library.
"""
from pathlib import Path

from cffi import FFI

ffibuilder = FFI()

ffibuilder.set_source("monetdbe._lowlevel",
                      """
#include "monetdb/monetdbe.h"
                      """,
                      libraries=['monetdbe'])

path = str(Path(__file__).parent / 'embed.h')

with open(path, 'r') as f:
    ffibuilder.cdef(f.read())

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
