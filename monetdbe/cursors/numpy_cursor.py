from monetdbe.cursors.cursor import Cursor  # type: ignore[attr-defined]
from typing import Union, Any, Iterator, Sequence, Mapping

import numpy as np

from monetdbe.row import Row
from monetdbe._cffi.internal import result_fetch_numpy


class NumpyCursor(Cursor):
    def __iter__(self) -> Iterator[Union[Row, Sequence[Any]]]:
        result = self.fetchall()

        for row in result:
            if self.connection.row_factory:  # type: ignore[union-attr]
                yield self.connection.row_factory(cur=self, row=tuple(row))  # type: ignore[union-attr]
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
        return result_fetch_numpy(self.connection.result)  # type: ignore[union-attr]

    def fetchall(self):
        result = self.fetchnumpy()
        if result:
            return list(np.vstack(list(result.values())).T)
        return []

    def write_csv(self, table, *args, **kwargs):
        return self.execute(f"select * from {table}").fetchdf().to_csv(*args, **kwargs)
