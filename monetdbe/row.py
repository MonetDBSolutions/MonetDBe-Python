from typing import Union, Generator, Optional, Any
from monetdbe.cursor import Cursor


class Row:
    def __init__(self, cur: Cursor, row: Union[tuple, Generator[Optional[Any], Any, None]]):
        if type(cur) != Cursor:
            raise TypeError

        self.cur = cur
        self.row = row

    def __iter__(self):
        self._iter = zip(self.row.__iter__(), self.cur.description.__iter__())
        return self

    def __next__(self):
        return next(self._iter)
