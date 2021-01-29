from .cursor import Cursor
from typing import Union, Any, Generator, Sequence, Mapping

import numpy as np

from monetdbe._cffi.internal import result_fetch_numpy


class NumpyCursor(Cursor):
    def __iter__(self) -> Generator[Union['Row', Sequence[Any]], None, None]:
        result = self.fetchall()

        for row in result:
            if self.connection.row_factory:
                yield self.connection.row_factory(cur=self, row=tuple(row))
            elif self.row_factory:  # Sqlite backwards compatibly
                yield self.row_factory(self, tuple(row))
            else:
                yield tuple(row)

    def fetchnumpy(self) -> Mapping[str, np.ndarray]:
        """
        Fetch all results and return a numpy array.

        like .fetchall(), but returns a numpy array.
        """
        self._check_connection()
        self._check_result()
        return result_fetch_numpy(self.connection.result)

    def fetchall(self):
        result = self.fetchnumpy()
        if result:
            return np.vstack(list(result.values())).T
        else:
            return []

    def write_csv(self, table, *args, **kwargs):
        return self.execute(f"select * from {table}").fetchdf().to_csv(*args, **kwargs)
