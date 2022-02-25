import unittest
import monetdbe
import pymonetdb  # type: ignore


class TestMapi(unittest.TestCase):
    def test_mapi(self):
        with monetdbe.connect(autocommit=True, host="localhost", port=0) as con:
            con.execute("CREATE TABLE IF NOT EXISTS test (x,y) AS VALUES (10,'foo'), (0, 'bar'), (20, 'baz'), (NULL,NULL);")

            remote_con = pymonetdb.connect(username="monetdb", password="monetdb", hostname="localhost", port=con.get_port(), database="in-memory")
            cursor = remote_con.cursor()
            cursor.execute("SELECT * FROM test WHERE x > 5 ORDER BY x")
            result = cursor.fetchall()
            self.assertEqual(result, [(10, 'foo'), (20, 'baz')])
