Application migration
=====================

In many situations there are already applications running for quite some time and
the question arises if it is worth to switch over to MonetDBe. In those cases,
the effort required should be kept to a minimum. Note that MonetDBe provides a wealth
of SQL features derived from Monetdb directly, i.e. enriched base types, 
controlled parallelism, persistent stored modules, UDFs,...
which are not necessarily available in the systems mentioned below.
Using such features may improve the performance of you program, but also could
hinder a reversion from a MonetDBe application into your hitherto favored system.

Migration starts with replacing all occurrences of the target system with `monetdbe` in the Python program.

Porting SQLite3 programs
------------------------

A plethora of programs are written in `SQLite 3 <https://www.sqlite.org/index.html>` and 
its website contains an extensive account on the particulars.  

The following functionality is a snapshot of the caveats you may run into
when porting to MonetDBe.
- SQLite is based on manifest typing, MonetDBe on rigid types.
- SQLite allows current access to the same local database using locking?
- No cross platform data exchange format (big- little- endians)
- `Thread safety <https://www.sqlite.org/threadsafe.html>` 
- `Copy statement <https://www.uniplot.de/documents/en/src/articles/SQLite.html#copy>` 
- *INTEGER PRIMARY KEY*  should be mapped to the SERIAL type in MonetDBe.
- *VACUUM* is not supported. Garbage collection is implicit.
- *EXPLAIN* is based on the MonetDB abstract machine.
- `*ON CONFLICT* <https://www.sqlite.org/lang_conflict.html>` not supported.
- `*REPLACE* <https://www.sqlite.org/lang_replace.html>` not supported
- `*ATTACH and DETACH <https://www.sqlite.org/lang_attach.html>` replaced by connect().`
- `Collating Sequences <https://www.sqlite.org/c3ref/create_collation.html>`.
- `FTS5 <https://www.sqlite.org/fts5.html.`.
- `Rtree <https://www.sqlite.org/rtree.html>`.

Porting DuckDB programs
-----------------------

DuckDB is a research prototype developed by the next generation of database researchers at
CWI. It is focused on data analytic workflows in an embedded setting with an emphasis on R.
Migration starts with replacing all occurrences of 'duckdb' with 'monetdbe'.

The following functionality is not supported by MonetDBe or contains syntax/semantic differences.
- `COPY into statement <https://duckdb.org/docs/data/csv>` 
- `Appender function <https://duckdb.org/docs/data/appender>` 
- `Loading parquet files <https://duckdb.org/docs/data/parquet>`  
- `R connector <//https://duckdb.org/docs/api/r>` 
- `JDBC connector <//https://duckdb.org/docs/api/java>` 
- `PRAGMA <https://duckdb.org/docs/sql/pragmas>` 
- `Pandas registration as SQL view <https://duckdb.org/docs/api/python>` 

Reporting issues
----------------

We highly appreciate user feed back for migrations undertaken in the MonetDB issue tracker on GitHub.
Both as a warning and best practices for those who follow, but also to assess the need for
features hitherto not available in MonetDBe

