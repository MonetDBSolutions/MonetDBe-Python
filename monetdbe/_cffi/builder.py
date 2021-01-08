"""
This is a build-time utility that will generate the monetdbe._lowlevel
CFFI bridging shared library.
"""
from pathlib import Path
from sys import platform

from cffi import FFI

ffibuilder = FFI()

# not all platforms support 128 bit (windows). Since CFFI cdefs dont support conditionals
# we need to do this a bit awkward:
monetdbe_types_template = """
typedef enum {{
 monetdbe_bool, monetdbe_int8_t, monetdbe_int16_t, monetdbe_int32_t, monetdbe_int64_t,
 {placeholder}
 monetdbe_size_t, monetdbe_float, monetdbe_double,
 monetdbe_str, monetdbe_blob,
 monetdbe_date, monetdbe_time, monetdbe_timestamp,
 monetdbe_type_unknown
}} monetdbe_types;
"""

if platform == 'win32':
    monetdbe_types = monetdbe_types_template.format(placeholder="")
else:
    monetdbe_types = monetdbe_types_template.format(placeholder="monetdbe_int128_t,")


lowlevel_source = """
#include "monetdb/monetdbe.h"
"""

ffibuilder.set_source("monetdbe._lowlevel", lowlevel_source, libraries=['monetdbe'])
path = str(Path(__file__).parent / 'embed.h')

with open(path, 'r') as f:
    cdef = monetdbe_types + f.read()
    ffibuilder.cdef(cdef)

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)
