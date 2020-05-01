from monetdbe import connect


con = connect()
cur = con.cursor()
cur.execute("CREATE TABLE test (x integer, y string)")
cur.execute("INSERT INTO test VALUES (42, 'Hello'), (NULL, 'World')")
cur.execute("SELECT x, y FROM test; ")
rows = cur.fetchall()
print(rows)
