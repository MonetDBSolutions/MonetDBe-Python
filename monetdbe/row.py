"""

"""
import collections.abc
from typing import Union, Generator, Optional, Any, List

from monetdbe.cursor import Cursor


class Row:
    """
    A Row is a non-standard SQLite compatible data container. It tries to mimic a tuple in most of its features.

    It supports mapping access by column name and index, iteration, representation, equality testing and len().

    If two Row objects have exactly the same columns and their members are equal, they compare equal.
    """
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

    def keys(self) -> List[str]:
        return [i.name for i in self.cur.description]


collections.abc.Sequence.register(Row)
