=====================
Application Migration
=====================

In many situations there are already applications running for quite some time and
the question arises if it is worth to switch over to MonetDB/e. In those cases,
the effort required should be kept to a minimum. Note that MonetDB/e provides a wealth
of SQL features derived from Monetdb directly, i.e. enriched base types, 
controlled parallelism, persistent stored modules, UDFs,...
which are not necessarily available in the systems mentioned below.
Using such features may improve the performance of you program, but also could
hinder a reversion from a MonetDB/e application into your hitherto favored system.


Porting SQLite3 programs
------------------------

A plethora of programs are written in `SQLite 3 <https://www.sqlite.org/index.html>`_ and 
its website contains an extensive account on the particulars.  

Migration starts with replacing all occurrences of the sqlite3 with `monetdbe` in the Python program.

The following functionality is not supported by MonetDB/e or contains syntax/semantic differences.

- SQLite is based on manifest typing, MonetDB/e on rigid types.
- SQLite allows current access to the same local database using file-based locking?
- No cross platform data exchange format (big- little- endians)
- `Thread safety <https://www.sqlite.org/threadsafe.html>`_ no specific control.
- `Copy statement <https://www.uniplot.de/documents/en/src/articles/SQLite.html#copy>`_ delimiters may be different.
- INTEGER PRIMARY KEY  should be mapped to the SERIAL type in MonetDB/e.
- VACUUM is not supported. Garbage collection is implicit.
- EXPLAIN is based on the MonetDB abstract machine.
- PRAGMAs are not recognized.
- `ON CONFLICT <https://www.sqlite.org/lang_conflict.html>`_ not supported.
- `REPLACE <https://www.sqlite.org/lang_replace.html>`_ not supported
- `ATTACH and DETACH <https://www.sqlite.org/lang_attach.html>`_ replaced by connect().
- `Collating Sequences <https://www.sqlite.org/c3ref/create_collation.html>`_.
- `JDBC connector <https://www.sqlite.org/java/raw/doc/overview.html?name=0a704f4b7294a3d63e6ea2b612daa3b997c4b5f1>`_.
- `FTS5 <https://www.sqlite.org/fts5.html>`_ not supported.
- `Rtree <https://www.sqlite.org/rtree.html>`_ not supported.

Porting DuckDB programs
-----------------------

[DuckDB](https://www.duckdb.org) is an embedded analytical data management system.
Migration starts with replacing all occurrences of 'duckdb' with 'monetdbe'.

The following functionality is not supported by MonetDB/e or contains syntax/semantic differences.

- `COPY into statement <https://duckdb.org/docs/data/csv>`_ uses a different delimiter structure.
- `Appender function <https://duckdb.org/docs/data/appender>`_ currently in C-version.
- `Loading parquet files <https://duckdb.org/docs/data/parquet>`_.
- `R connector <https://duckdb.org/docs/api/r>`_.
- `JDBC connector <https://duckdb.org/docs/api/java>`_.
- `PRAGMA <https://duckdb.org/docs/sql/pragmas>`_.
- `Pandas registration as SQL view <https://duckdb.org/docs/api/python>`_.

Reporting issues
----------------

We highly appreciate user feed back for migrations undertaken in the MonetDB issue tracker on GitHub
or stackoverflow.
Both as a warning and best practices for those who follow, but also to assess the need for
features hitherto not available in MonetDB/e

