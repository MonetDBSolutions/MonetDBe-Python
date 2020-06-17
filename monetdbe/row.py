"""

"""
import collections.abc
from typing import Union, Generator, Optional, Any, Tuple

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

        self._cur = cur
        self._row = tuple(row)

        if self._cur.description:
            self._keys = tuple(i.name for i in self._cur.description)
        else:
            self._keys = tuple()

        self._key_map = dict(zip(self._keys, range(len(self._keys))))

    def __hash__(self):
        return hash(self._keys) ^ hash(self._keys)

    def __eq__(self, other) -> bool:
        if isinstance(other, type(self)):
            a = self._keys == other._keys
            b = self._row == other._row
            return a & b
        else:
            return False

    def __iter__(self):
        # return zip(self.cur.description.__iter__(), self.row.__iter__())
        return self._row.__iter__()

    def __len__(self):
        return len(self._row)

    def __getitem__(self, item):
        if isinstance(item, (int, slice)):
            return self._row.__getitem__(item)
        elif isinstance(item, str):
            try:
                return self._row.__getitem__(self._key_map[item])
            except KeyError:
                raise IndexError from None
        else:
            raise TypeError(f"type {type(item)} not supported")

    def keys(self) -> Tuple[Any]:
        # todo (gijs): type
        return self._keys  # type: ignore


collections.abc.Sequence.register(Row)
