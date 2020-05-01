from monetdbe import connect


def test_simple():
    con = connect()
    cur = con.cursor()
    cur.execute("CREATE TABLE test (x integer, y string)")
    cur.execute("INSERT INTO test VALUES (42, 'Hello'), (NULL, 'World')")
    cur.execute("SELECT x, y FROM test; ")
    rows = list(cur.fetchall())
    print(rows)


if __name__ == '__main__':
    test_simple()
