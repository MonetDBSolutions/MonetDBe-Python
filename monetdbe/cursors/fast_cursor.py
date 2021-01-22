from .cursor import Cursor
from typing import Mapping, cast
import numpy as np
from itertools import repeat
import pandas as pd

from monetdbe._cffi.internal import result_fetch_numpy


class FastCursor(Cursor):
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

        iters = [iter(i) for i in result.values()]

        def traverse():
            while True:
                yield [next(i) for i in iters]

        return list(traverse)


    def write_csv(self, table, *args, **kwargs):
        return self.execute(f"select * from {table}").fetchdf().to_csv(*args, **kwargs)