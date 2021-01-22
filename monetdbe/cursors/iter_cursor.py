from .cursor import Cursor
from typing import Tuple, Optional, Union, Any, Generator, Sequence, List, TYPE_CHECKING, Mapping
from monetdbe.exceptions import InterfaceError
from monetdbe._cffi.internal import result_fetch
import numpy as np

if TYPE_CHECKING:
    from monetdbe.row import Row


class IterCursor(Cursor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fetch_generator: Optional[Generator] = None

    def __iter__(self) -> Generator[Union['Row', Sequence[Any]], None, None]:
        # we import this late, otherwise the whole monetdbe project is unimportable
        # if we don't have access to monetdbe shared library
        from monetdbe._cffi.convert import extract

        self._check_connection()

        if not self.connection.result:
            raise StopIteration

        columns = list(map(lambda x: result_fetch(self.connection.result, x), range(self.connection.result.ncols)))
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

    def fetchmany(self, size=None):
        """
        Fetch the next set of rows of a query result, returning a list of tuples). An empty sequence is returned when
        no more rows are available.

        args:
            size: The number of rows to fetch. Fewer rows may be returned.

        Returns: A number of rows from a query result as a list of tuples

        Raises:
            Error: If the previous call to .execute*() did not produce any result set or no call was issued yet.

        """
        self._check_connection()
        # self._check_result() sqlite test suite doesn't want us to bail out

        if not self.connection.result:
            return []

        if not size:
            size = self.arraysize
        if not self._fetch_generator:
            self._fetch_generator = self.__iter__()

        rows = []
        for i in range(size):
            try:
                rows.append(next(self._fetch_generator))
            except StopIteration:
                break
        return rows

    def fetchone(self) -> Optional[Union['Row', Sequence]]:
        """
        Fetch the next row of a query result set, returning a single tuple, or None when no more data is available.

        Returns:
            One row from a result set.

        Raises:
            Error: If the previous call to .execute*() did not produce any result set or no call was issued yet.

        """
        self._check_connection()
        # self._check_result() sqlite test suite doesn't want us to bail out

        if not self.connection.result:
            return None

        if not self._fetch_generator:
            self._fetch_generator = self.__iter__()
        try:
            return next(self._fetch_generator)
        except StopIteration:
            return None

    def fetchnumpy(self) -> Mapping[str, np.ndarray]:
        self._check_connection()
        self._check_result()
        all = self.fetchall()
        names = (d.name for d in self.description)
        flipped = zip(*all)
        return {k: v for k, v in zip(names, flipped)}
