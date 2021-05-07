============
Introduction
============

Harnessing the power of a database server for data analytics into a single shared library is the first step on the road to
benefit from the servers' performance features. MonetDB/e is such a core library of MonetDB.
We started out with a small C-API a few years back to build our first embedded applications using it.

However, the MonetDB eco system also provides APIs to Python, Java, Ruby, R, PhP… They all rely on the JDBC/ODBC layer
for interaction with the server. A library that simply launches a database server in the background and
then connect to it using the JDBC/ODBC layer is evidently not the way to go. It would create too much interprocess
communication and potentially a lot of data shipping. A truly embedded database system dares to live in the same
address space as the application. Of course, this comes with shared responsibilities.

Therefore, our next target was to make the MonetDB functionality available as a simple drop-in library in Python, called monetdbe.
Python has a clearly defined database interface, called DB-API 2.0, and an interface aligned with SQLite.
Furthermore, with a claimed installed base of SQLite of more than one billion there is a lot of code out there 
and users comfortably with its programmatic interface. 
Likewise, the Pandas/Numpy extensions only provide a subset of the functionality offered by a database systems, leaving
much of the work to the programmer to  cast  a query execution plans into code lines, manage indices, and handling huge IO
using chunks.
The goal for MonetDB/e was set to follow the Python/SQLite3 interface as much as possible and this way opens
the toolchest of a power database engine to relieve the programmer from these laborate tasks.

We followed a test-driven approach by starting with the test suite for Python/SQLite 3 and working our way through all
the unit tests covered. The complete list is included in the .../tests directory. Several tests where skipped, because
they are too tightly coupled with the SQLite semantics. We keep a list 
of `open issues <https://github.com/MonetDBSolutions/MonetDB/e-Python/issues>`_  and the planning for the next milestones.

For example, the row factory functions are not supported. They coped with the limited set of data types
supported by SQLite, which triggers an (expensive) call back method when accessing the elements in 
a result set. That works for a limited number of rows, but is a performance drain when you work with
millions of rows. MonetDB/e has a much richer basic type system that includes e.g. the temporals, UUIDS, JSON ond DECIMAL out of the box.
Likewise, transaction management in MonetDB/e is based on `MVCC <https://www.monetdb.org/blog/optimistic-concurrency-control>`_
without explicit levels of isolations.  The latter a remnant of the past in SQLite when systems were based on explicit locking.

How does it work
================

Using the library starts with simply getting the module into your Python environment, ‘pip install monetdbe’.
A minimal example to see if everything works as expected::

    import monetdbe
    conn = monetdbe.connect(':memory:')
    c = conn.cursor()
    c.execute('SELECT count(*) FROM tables')
    print(c.fetchone())

A collection of example programs written in C and Python
can be found in the `monetdbe-examples <https://github.com/MonetDBSolutions/monetdbe-examples>`_ repository.

What are the perks
==================

Capitalizing the MonetDB server code base makes amongst others the following features available for an embedded version:

- No client-server communication overhead.
- No result-set serialiszation, but binary column-ary access.
- Full use of the multi-core parallel query execution.
- Hassle free data auto-indexing.
- Dictionary compressed string handling.
- Seamless integration with the programming language, e,g, dataframes/numpy.
- Simple user control over the resources.
- Working with :memory: databases with controlled RAM footprint.
- Hybrid set up with concurrent ``:memory:``, local storage  and server-based storage.
- Boosting your data analytics programs with stateful User Defined Functions.
- Extended base types, DECIMAL, JSON, blob, uuid, boolean
- Statistics, windowing functions, grouped sets, cube, and rollup.
- Persistent stored modules of SQL procedures/functions
- SQL-standard compliance and many Postgresql extensions.
- Streaming input/output handling of compressed files.
- Hot snapshots for point-in-time  backup/recovery.

Storage options
===============
One of the key factors in an embedded database system is the location of the persistent data, if it needs to persist at all.  In
MonetDB/e we opted for a simple interface based on URLs, ``:memory:``, ``/OSpath/directory``, ``file://filename?withoptions``, ``monetdb://mapi_host:port/db?withoptions``. 
The benefit of this approach is that one can start developing the application with an in memory only, ``:memory:``, storage and switch to
the local directory or server version by simply changing the connection point.
The first released implementation of MonetDB/e is limited to a single ``:memory:`` or a local directory.


Debugging and stability
=======================

Using an embedded database library also comes with mutual responsibility. Unlike a server solution, your program could 
easily lead to a corrupted database with peek/pook in the underlying database structures (using C-functions).
Such a corruption may be not immediately be detected. This can be partly countered by taking regular database backups.

For debugging you can rely on the logging scheme available in every MonetDB/e instance or the Python logging module.
Alternatively, the Python debugger gives information up to the point the code switches to the underlying C function.
Consider this a natural barrier not to cross, because the database kernel code is highly complex.

For stability we deploy `SQLsmith <https://github.com/anse1/sqlsmith>`_ and `SQLancer <https://github.com/sqlancer/sqlancer>`_ 
on a daily basis to isolate corner cases that might havoc the system. 
As an aside, we use a Continuous Integration framework based on `buildbot <https://buildbot.net/>`_ for stability and regression testing on two dozen platforms.

What are the caveats
====================

There are a few caveats to the approach presented. SQLite and MonetDB/e do not align 100% on the same interpretation of
the SQL standard. MonetDB/e is much more strict. This may result in minor differences in error handling or even some surprises
in the results. An overview is provided in the :ref:`Application Migration` section.

REMINDER, the Python package monetdbe is a *first-release* made available from PyPi. You don’t need to install MonetDB itself.
Missing features and glitches can be be reported using the issue tracker of the monetdbe-python repository on Github..

When to use an embedded database
================================

In addition to the list above, use an embedded system if you want a quick starter on using a SQL-based system.
In particular if you are working with large tables calling for a pre-filterings, aggregation, and transformation of
a relational table before you hand it over to e.g. a machine learning model.

However, a database system that shares the memory space with the application code may cause unexpected interference.
For example, it is relatively easy to overwrite its internal structures and thereby leaving a corrupted database behind.
Or, there may be resource wars between application logic and the database kernel as it fights over RAM and CPU cores.

MonetDB/e comes with shared responsibility. It works best if you need a database for analytics where you can
either easily reload the database from an archive or use the point-in-time hot snapshot/backup methods. It is also a great tool
to embark on application development without the need for a shared server in the background.

Some people also translate ease of use into providing a single file as the storage container for the database
to simplify sharing a database.
Even SQLite relieved this requirement by packaging multiple databases into a single archive file.
MonetDB/e works with a local/remote directory. There are many tools to package and transfer them to enable
cloning and sharing the database with your peers. 

MonetDB/e roadmap
=================

- MonetDB/e as proxy to a server
- Java jar drop=in
- Embedded version for R
- Import of (mini)parquet and Arrow files
- Remote query processing over multiple ``:memory:`` instances
- Using MonetDB/e as a JDBC/ODBC endpoint

