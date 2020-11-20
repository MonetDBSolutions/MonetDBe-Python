from typing import NewType

from monetdbe._lowlevel import ffi

monetdbe_result = NewType('monetdbe_result', ffi.CData)
monetdbe_database = NewType('monetdbe_database', ffi.CData)
monetdbe_column = NewType('monetdbe_column', ffi.CData)
char_p = NewType('char_p', ffi.CData)