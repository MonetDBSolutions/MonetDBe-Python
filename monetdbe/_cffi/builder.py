"""
This is a build-time utility that will generate the monetdbe._lowlevel
CFFI bridging shared library.
"""
from pathlib import Path
from sys import platform

from cffi import FFI
from jinja2 import Template

win32 = platform == 'win32'
default = True

source = """
#include "monetdb/monetdbe.h"
"""

# the ffibuilder object needs to exist and be configured in the module namespace so setup.py can reach it
ffibuilder = FFI()
ffibuilder.set_source("monetdbe._lowlevel", source, libraries=['monetdbe'])
embed_path = str(Path(__file__).parent / 'embed.h.j2')

with open(embed_path, 'r') as f:
    content = f.read()
    print(content)
    template = Template(content)
    cdef = template.render(win32=win32, default=default)
    ffibuilder.cdef(cdef)

def build():
    ffibuilder.compile(verbose=True)


if __name__ == "__main__":
    build()
