from monetdbe._cffi.frontend import Frontend

q1 = "CREATE TABLE test (b bool, t tinyint, s smallint, x integer, l bigint,h hugeint, f float, d double, y string)"
q2 = "INSERT INTO test VALUES (TRUE, 42, 42, 42, 42, 42, 42.42, 42.42, 'Hello'), (NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'World')"
q3 = "SELECT b, t, s, x, l, h, f, d, y FROM test; "

f = Frontend()
f.open()
f.query(q1)
f.query(q2)
result, rows = f.query(q3, make_result=True)
f.cleanup_result(result)
statement = f.prepare("SELECT b, t FROM test where t = ?; ")
f.bind(statement, 42)
f.execute(statement)
"""

	monetdbe_statement *stmt = NULL;
	if ((err = monetdbe_prepare(mdbe, "SELECT b, t FROM test where t = ?; ", &stmt)) != NULL)
		error(err)
	char s = 42;
	if ((err = monetdbe_bind(stmt, &s, 0)) != NULL)
		error(err)
	if ((err = monetdbe_execute(stmt, &result, NULL)) != NULL)
		error(err)
	fprintf(stdout, "Query result with %zu cols and %"PRId64" rows\n", result->ncols, result->nrows);
	if ((err = monetdbe_cleanup_result(mdbe, result)) != NULL)
		error(err)
	if ((err = monetdbe_cleanup_statement(mdbe, stmt)) != NULL)
		error(err)

	if (monetdbe_close(mdbe))
		error("Failed to close database")
	return 0;
}

"""