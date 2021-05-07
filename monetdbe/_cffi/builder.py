"""
This is a build-time utility that will generate the monetdbe._lowlevel
CFFI bridging shared library.
"""
from pathlib import Path
from sys import platform
from os import environ
from cffi import FFI
from jinja2 import Template


monetdb_branch = environ.get("MONETDB_BRANCH", "default")
print(f"\n**MONETDB**: We are assuming you are building against MonetDB branch {monetdb_branch}")
print("**MONETDB**: If this is incorrect, set the MONETDB_BRANCH environment variable during monetdbe-python build\n")


default = monetdb_branch.lower() in ("default", "jul2021")
win32 = platform == 'win32'


source = """
#include "monetdb/monetdbe.h"
"""


# the ffibuilder object needs to exist and be configured in the module namespace so setup.py can reach it
ffibuilder = FFI()
ffibuilder.set_source("monetdbe._lowlevel", source, libraries=['monetdbe'])
embed_path = str(Path(__file__).parent / 'embed.h.j2')


with open(embed_path, 'r') as f:
    content = f.read()
    template = Template(content)
    cdef = template.render(win32=win32, default=default)
    ffibuilder.cdef(cdef)


def build():
    ffibuilder.compile(verbose=True)


if __name__ == "__main__":
    build()
