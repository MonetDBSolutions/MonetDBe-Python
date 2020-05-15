import collections.abc
from typing import Union, Generator, Optional, Any

from monetdbe.cursor import Cursor


class Row:
    def __init__(self, cur: Cursor, row: Union[tuple, Generator[Optional[Any], Any, None]]):
        if type(cur) != Cursor:
            raise TypeError

        self.cur = cur
        self.row = list(row)

    def __iter__(self):
        # return zip(self.cur.description.__iter__(), self.row.__iter__())
        return self.row.__iter__()

    def __len__(self):
        return len(self.row)

    def __getitem__(self, item):
        return self.row.__getitem__(item)


collections.abc.Sequence.register(Row)
