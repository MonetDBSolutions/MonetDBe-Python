Application migration
=====================

In many situations there are already applications running for quite some time and
the question arrises if it is worth to switch over to MonetDBe. In those cases,
the effort required should be kept to a minimum. Note that MonetDBe provides a wealth
of SQL features derived from Monetdb directly, i.e. enriched base types, 
controlled parallelism, persistent stored modules, UDFs,...
which are not necessarily available in the systems mentioned below.
Using such features may improve the performance of you program, but also could
hinder a revert back from MonetDBe into your current favored environment.

Migration starts with replacing all occurrences of the target program with monetdbe in the Python program.

Porting SQLite3 programs
------------------------

A plethora of programs are written in `SQLite 3 <https://www.sqlite.org/index.html>` and its website contains an extensive account on
the particulars.  
The caveats to encounter migration to a MonetDBe program are:

- `*Single threading<>` Multi-threading execution is considered a no go, which can be overruled with a
property setting. MonetDBe is inheritantly multi-htreaded. There is no need to enable it. Running in single threaded mode
is support by passing the 'workers=1' in the connection string.
- `*Copy statement* <https://www.uniplot.de/documents/en/src/articles/SQLite.html#copy>` A conflict-algorithm is 
not supported.
- *INTEGER PRIMARY KEY*  should be mapped to the SERIAL type in MonetDBe.
- *VACUUM* is not supported in MonetDBe. Garbage collection is implicit.

Porting DuckDB programs
-----------------------

DuckDB is a research prototype developed by the next generation of MonetDB researchers at
CWI. It is focussed on data analytics in an embedded setting, with a particular emphasis on R.
Migration starts with replacing all occurrences of duckdb with monetdbe.

The caveats to encounter migration to a MonetDBe program are:
- `*Copy into statement* <http:>` has a slightly different syntax.
- `*Parquet files* <http://>`  are not yet supported by MonetDBe.

Reporting issues
----------------

We highly appreciate user feed back for migrations undertaken. Both as a warning
and best practices for those who follow, but also to assess the need for
features hitherto not available in MonetDBe. Please fill out an `issue form <http://tobedefined.nl>`
i
