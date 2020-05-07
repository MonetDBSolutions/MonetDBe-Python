from monetdbe import connect


def test_simple():
    con = connect()
    cur = con.cursor()
    cur.execute("CREATE TABLE test (x integer, y string)")
    cur.execute("INSERT INTO test VALUES (42, 'Hello'), (NULL, 'World')")
    cur.execute("SELECT x, y FROM test; ")
    rows = list(cur.fetchall())
    print(rows)

    con2 = connect()
    cur2 = con.cursor()
    cur2.execute("CREATE TABLE test (x integer, y string)")
    cur2.execute("INSERT INTO test VALUES (42, 'Hello'), (NULL, 'World')")
    cur2.execute("SELECT x, y FROM test; ")
    rows2 = list(cur.fetchall())
    print(rows2)


if __name__ == '__main__':
    test_simple()
