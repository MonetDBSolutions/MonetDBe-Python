# type: ignore[union-attr]
from .base_cursor import BaseCursor
from typing import Union, Any, Iterator, Sequence, List, Mapping, TYPE_CHECKING
from monetdbe.exceptions import InterfaceError
from monetdbe._cffi.internal import result_fetch
import numpy as np

if TYPE_CHECKING:
    from monetdbe.row import Row


class IterCursor(BaseCursor):
    def __iter__(self) -> Iterator[Union['Row', Sequence[Any]]]:
        # we import this late, otherwise the whole monetdbe project is unimportable
        # if we don't have access to monetdbe shared library
        from monetdbe._cffi.convert import extract

        self._check_connection()

        if not self.connection.result:
            raise StopIteration

        columns = list(map(lambda x: result_fetch(self.connection.result, x), range(self.connection.result.ncols)))   # type: ignore[union-attr]
        for r in range(self.connection.result.nrows):
            row = tuple(extract(rcol, r, self.connection.text_factory) for rcol in columns)
            if self.connection.row_factory:
                yield self.connection.row_factory(cur=self, row=row)
            elif self.row_factory:  # Sqlite backwards compatibly
                yield self.row_factory(self, row)
            else:
                yield row

    def fetchall(self) -> List[Union['Row', Sequence]]:
        """
        Fetch all (remaining) rows of a query result, returning them as a list of tuples).

        Returns:
            all (remaining) rows of a query result as a list of tuples

        Raises:
            Error: If the previous call to .execute*() did not produce any result set or no call was issued yet.
        """
        self._check_connection()

        # note (gijs): sqlite test suite doesn't want us to raise exception here, so for now I disable this
        # self._check_result()

        if not self.connection.consistent:
            raise InterfaceError("Tranaction rolled back, state inconsistent")

        if not self.connection.result:
            return []

        rows = [i for i in self]
        self.connection.result = None
        return rows

    def fetchnumpy(self) -> Mapping[str, np.ndarray]:
        self._check_connection()
        self._check_result()
        all_ = self.fetchall()
        names = (d.name for d in self.description)
        flipped = zip(*all_)
        return {k: v for k, v in zip(names, flipped)}
