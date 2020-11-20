from monetdbe._cffi.frontend import Frontend

q1 = "CREATE TABLE test (b bool, t tinyint, s smallint, x integer, l bigint,h hugeint, f float, d double, y string)"
q2 = "INSERT INTO test VALUES (TRUE, 42, 42, 42, 42, 42, 42.42, 42.42, 'Hello'), (NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'World')"

f = Frontend()
f.open()
f.query(q1)
f.query(q2)
statement = f.prepare("SELECT b, t FROM test where t = ?; ")
f.bind(statement, 42, 0)
f.execute(statement)
f.cleanup_statement(statement)