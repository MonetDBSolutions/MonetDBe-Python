# -*- coding: iso-8859-1 -*-
# monetdbe/test/test_dbapi.py: tests for DB-API compliance
#
# Copyright (C) 2004-2010 Gerhard Häring <gh@ghaering.de>
#
# This file is part of pymonetdbe.
#
# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.

import threading
import unittest
import monetdbe as monetdbe

from test.support import TESTFN, rmtree


class ModuleTests(unittest.TestCase):
    def test_APILevel(self):
        self.assertEqual(monetdbe.apilevel, "2.0",
                         "apilevel is %s, should be 2.0" % monetdbe.apilevel)

    def test_ThreadSafety(self):
        self.assertEqual(monetdbe.threadsafety, 1,
                         "threadsafety is %d, should be 1" % monetdbe.threadsafety)

    def test_ParamStyle(self):
        self.assertEqual(monetdbe.paramstyle, "qmark",
                         "paramstyle is '%s', should be 'qmark'" %
                         monetdbe.paramstyle)

    def test_Warning(self):
        self.assertTrue(issubclass(monetdbe.Warning, Exception),
                        "Warning is not a subclass of Exception")

    def test_Error(self):
        self.assertTrue(issubclass(monetdbe.Error, Exception),
                        "Error is not a subclass of Exception")

    def test_InterfaceError(self):
        self.assertTrue(issubclass(monetdbe.InterfaceError, monetdbe.Error),
                        "InterfaceError is not a subclass of Error")

    def test_DatabaseError(self):
        self.assertTrue(issubclass(monetdbe.DatabaseError, monetdbe.Error),
                        "DatabaseError is not a subclass of Error")

    def test_DataError(self):
        self.assertTrue(issubclass(monetdbe.DataError, monetdbe.DatabaseError),
                        "DataError is not a subclass of DatabaseError")

    def test_OperationalError(self):
        self.assertTrue(issubclass(monetdbe.OperationalError, monetdbe.DatabaseError),
                        "OperationalError is not a subclass of DatabaseError")

    def test_IntegrityError(self):
        self.assertTrue(issubclass(monetdbe.IntegrityError, monetdbe.DatabaseError),
                        "IntegrityError is not a subclass of DatabaseError")

    def test_InternalError(self):
        self.assertTrue(issubclass(monetdbe.InternalError, monetdbe.DatabaseError),
                        "InternalError is not a subclass of DatabaseError")

    def test_ProgrammingError(self):
        self.assertTrue(issubclass(monetdbe.ProgrammingError, monetdbe.DatabaseError),
                        "ProgrammingError is not a subclass of DatabaseError")

    def test_NotSupportedError(self):
        self.assertTrue(issubclass(monetdbe.NotSupportedError,
                                   monetdbe.DatabaseError),
                        "NotSupportedError is not a subclass of DatabaseError")


class ConnectionTests(unittest.TestCase):

    def setUp(self):
        self.cx = monetdbe.connect(":memory:")
        cu = self.cx.cursor()
        # todo/note (Gijs): made ID auto_increment
        cu.execute("create table test(id integer auto_increment primary key, name text)")
        cu.execute("insert into test(name) values (?)", ("foo",))

    def tearDown(self):
        self.cx.close()

    @unittest.skip("TODO: Not yet implemented, see issue #4")
    def test_Commit(self):
        self.cx.commit()

    @unittest.skip("TODO: Not yet implemented, see issue #4")
    def test_CommitAfterNoChanges(self):
        """
        A commit should also work when no changes were made to the database.
        """
        self.cx.commit()
        self.cx.commit()

    @unittest.skip("TODO (gijs): Not yet implemented")
    def test_Rollback(self):
        self.cx.rollback()

    @unittest.skip("TODO (gijs): Not yet implemented")
    def test_RollbackAfterNoChanges(self):
        """
        A rollback should also work when no changes were made to the database.
        """
        self.cx.rollback()
        self.cx.rollback()

    def test_Cursor(self):
        cu = self.cx.cursor()

    def test_FailedOpen(self):
        YOU_CANNOT_OPEN_THIS = "/foo/bar/bla/23534/mydb.db"
        with self.assertRaises(monetdbe.OperationalError):
            con = monetdbe.connect(YOU_CANNOT_OPEN_THIS)

    def test_Close(self):
        self.cx.close()

    def test_Exceptions(self):
        # Optional DB-API extension.
        self.assertEqual(self.cx.Warning, monetdbe.Warning)
        self.assertEqual(self.cx.Error, monetdbe.Error)
        self.assertEqual(self.cx.InterfaceError, monetdbe.InterfaceError)
        self.assertEqual(self.cx.DatabaseError, monetdbe.DatabaseError)
        self.assertEqual(self.cx.DataError, monetdbe.DataError)
        self.assertEqual(self.cx.OperationalError, monetdbe.OperationalError)
        self.assertEqual(self.cx.IntegrityError, monetdbe.IntegrityError)
        self.assertEqual(self.cx.InternalError, monetdbe.InternalError)
        self.assertEqual(self.cx.ProgrammingError, monetdbe.ProgrammingError)
        self.assertEqual(self.cx.NotSupportedError, monetdbe.NotSupportedError)

    @unittest.skip("TODO (gijs): Not yet implemented")
    def test_InTransaction(self):
        # Can't use db from setUp because we want to test initial state.
        cx = monetdbe.connect(":memory:")
        cu = cx.cursor()
        self.assertEqual(cx.in_transaction, False)
        cu.execute("create table transactiontest(id integer primary key, name text)")
        self.assertEqual(cx.in_transaction, False)
        cu.execute("insert into transactiontest(name) values (?)", ("foo",))
        self.assertEqual(cx.in_transaction, True)
        cu.execute("select name from transactiontest where name=?", ["foo"])
        row = cu.fetchone()
        self.assertEqual(cx.in_transaction, True)
        cx.commit()
        self.assertEqual(cx.in_transaction, False)
        cu.execute("select name from transactiontest where name=?", ["foo"])
        row = cu.fetchone()
        self.assertEqual(cx.in_transaction, False)

    def test_InTransactionRO(self):
        with self.assertRaises(AttributeError):
            self.cx.in_transaction = True

    def test_OpenWithPathLikeObject(self):
        """ Checks that we can successfully connect to a database using an object that
            is PathLike, i.e. has __fspath__(). """
        self.addCleanup(rmtree, TESTFN)

        class Path:
            def __fspath__(self):
                return TESTFN

        path = Path()
        with monetdbe.connect(path) as cx:
            cx.execute('create table test(id integer)')

    @unittest.skip("TODO: Not yet implemented, see issue #22")
    def test_OpenUri(self):
        self.addCleanup(rmtree, TESTFN)
        with monetdbe.connect(TESTFN) as cx:
            cx.execute('create table test(id integer)')
        with monetdbe.connect('file:' + TESTFN, uri=True) as cx:
            cx.execute('insert into test(id) values(0)')
        with monetdbe.connect('file:' + TESTFN + '?mode=ro', uri=True) as cx:
            with self.assertRaises(monetdbe.OperationalError):
                cx.execute('insert into test(id) values(1)')


class CursorTests(unittest.TestCase):
    def setUp(self):
        self.cx = monetdbe.connect(":memory:")
        self.cu = self.cx.cursor()

        # todo/note (Gijs): changed income type from number to float and made ID auto_increment
        self.cu.execute(
            "create table test(id integer auto_increment primary key, name text, "
            "income float, unique_test text unique)"
        )
        self.cu.execute("insert into test(name) values (?)", ("foo",))

    def tearDown(self):
        self.cu.close()
        self.cx.close()

    def test_ExecuteNoArgs(self):
        self.cu.execute("delete from test")

    def test_ExecuteIllegalSql(self):
        with self.assertRaises(monetdbe.OperationalError):
            self.cu.execute("select asdf")

    def test_ExecuteTooMuchSql(self):
        with self.assertRaises(monetdbe.Warning):
            self.cu.execute("select 5+4; select 4+5")

    def test_ExecuteTooMuchSql2(self):
        self.cu.execute("select 5+4; -- foo bar")

    def test_ExecuteTooMuchSql3(self):
        self.cu.execute("""
            select 5+4;

            /*
            foo
            */
            """)

    def test_ExecuteWrongSqlArg(self):
        with self.assertRaises(TypeError):
            self.cu.execute(42)

    def test_ExecuteArgInt(self):
        self.cu.execute("insert into test(id) values (?)", (42,))

    def test_ExecuteArgFloat(self):
        self.cu.execute("insert into test(income) values (?)", (2500.32,))

    def test_ExecuteArgString(self):
        self.cu.execute("insert into test(name) values (?)", ("Hugo",))

    @unittest.skip("todo: not yet supported, see issue #21")
    def test_ExecuteArgStringWithZeroByte(self):
        self.cu.execute("insert into test(name) values (?)", ("Hu\x00go",))

        self.cu.execute("select name from test where id=?", (self.cu.lastrowid,))
        row = self.cu.fetchone()
        self.assertEqual(row[0], "Hu\x00go")

    def test_ExecuteNonIterable(self):
        with self.assertRaises(ValueError) as cm:
            self.cu.execute("insert into test(id) values (?)", 42)
        self.assertEqual(str(cm.exception), "parameters '42' type '<class 'int'>' not supported")

    def test_ExecuteWrongNoOfArgs1(self):
        # too many parameters
        with self.assertRaises(monetdbe.ProgrammingError):
            self.cu.execute("insert into test(id) values (?)", (17, "Egon"))

    def test_ExecuteWrongNoOfArgs2(self):
        # too little parameters
        with self.assertRaises(monetdbe.ProgrammingError):
            self.cu.execute("insert into test(id) values (?)")

    def test_ExecuteWrongNoOfArgs3(self):
        # no parameters, parameters are needed
        with self.assertRaises(monetdbe.ProgrammingError):
            self.cu.execute("insert into test(id) values (?)")

    def test_ExecuteParamList(self):
        self.cu.execute("insert into test(name) values ('foo')")
        self.cu.execute("select name from test where name=?", ["foo"])
        row = self.cu.fetchone()
        self.assertEqual(row[0], "foo")

    def test_ExecuteParamSequence(self):
        class L(object):
            def __len__(self):
                return 1

            def __getitem__(self, x):
                assert x == 0
                return "foo"

        self.cu.execute("insert into test(name) values ('foo')")
        self.cu.execute("select name from test where name=?", L())
        row = self.cu.fetchone()
        self.assertEqual(row[0], "foo")

    def test_ExecuteDictMapping(self):
        self.cu.execute("insert into test(name) values ('foo')")
        self.cu.execute("select name from test where name=:name", {"name": "foo"})
        row = self.cu.fetchone()
        self.assertEqual(row[0], "foo")

    def test_ExecuteDictMapping_Mapping(self):
        class D(dict):
            def __missing__(self, key):
                return "foo"

        self.cu.execute("insert into test(name) values ('foo')")
        self.cu.execute("select name from test where name=:name", D())
        row = self.cu.fetchone()
        self.assertEqual(row[0], "foo")

    def test_ExecuteDictMappingTooLittleArgs(self):
        self.cu.execute("insert into test(name) values ('foo')")
        with self.assertRaises(monetdbe.ProgrammingError):
            self.cu.execute("select name from test where name=:name and id=:id", {"name": "foo"})

    def test_ExecuteDictMappingNoArgs(self):
        self.cu.execute("insert into test(name) values ('foo')")
        with self.assertRaises(monetdbe.ProgrammingError):
            self.cu.execute("select name from test where name=:name")

    def test_ExecuteDictMappingUnnamed(self):
        self.cu.execute("insert into test(name) values ('foo')")
        with self.assertRaises(monetdbe.ProgrammingError):
            self.cu.execute("select name from test where name=?", {"name": "foo"})

    def test_Close(self):
        self.cu.close()

    def test_RowcountExecute(self):
        self.cu.execute("delete from test")
        self.cu.execute("insert into test(name) values ('foo')")
        self.cu.execute("insert into test(name) values ('foo')")
        self.cu.execute("update test set name='bar'")
        self.assertEqual(self.cu.rowcount, 2)

    @unittest.skip("we skip this test, since we actually *do* know the rowcount")
    def test_RowcountSelect(self):
        """
        pymonetdbe does not know the rowcount of SELECT statements, because we
        don't fetch all rows after executing the select statement. The rowcount
        has thus to be -1.
        """
        self.cu.execute("select 5 union select 6")
        self.assertEqual(self.cu.rowcount, -1)

    def test_RowcountExecutemany(self):
        self.cu.execute("delete from test")
        self.cu.executemany("insert into test(name) values (?)", [(1,), (2,), (3,)])
        self.assertEqual(self.cu.rowcount, 3)

    def test_TotalChanges(self):
        self.cu.execute("insert into test(name) values ('foo')")
        self.cu.execute("insert into test(name) values ('foo')")
        self.assertLess(2, self.cx.total_changes, msg='total changes reported wrong value')

    # Checks for executemany:
    # Sequences are required by the DB-API, iterators
    # enhancements in pymonetdbe.

    def test_ExecuteManySequence(self):
        self.cu.executemany("insert into test(income) values (?)", [(x,) for x in range(100, 110)])

    def test_ExecuteManyIterator(self):
        class MyIter:
            def __init__(self):
                self.value = 5

            def __next__(self):
                if self.value == 10:
                    raise StopIteration
                else:
                    self.value += 1
                    return (self.value,)

        self.cu.executemany("insert into test(income) values (?)", MyIter())

    def test_ExecuteManyGenerator(self):
        def mygen():
            for i in range(5):
                yield (i,)

        self.cu.executemany("insert into test(income) values (?)", mygen())

    def test_ExecuteManyWrongSqlArg(self):
        with self.assertRaises(TypeError):
            self.cu.executemany(42, [(3,)])

    def test_ExecuteManySelect(self):
        with self.assertRaises(monetdbe.ProgrammingError):
            self.cu.executemany("select ?", [(3,)])

    def test_ExecuteManyNotIterable(self):
        with self.assertRaises(TypeError):
            self.cu.executemany("insert into test(income) values (?)", 42)

    def test_FetchIter(self):
        # Optional DB-API extension.
        self.cu.execute("delete from test")
        self.cu.execute("insert into test(id) values (?)", (5,))
        self.cu.execute("insert into test(id) values (?)", (6,))
        self.cu.execute("select id from test order by id")
        lst = []
        for row in self.cu:
            lst.append(row[0])
        self.assertEqual(lst[0], 5)
        self.assertEqual(lst[1], 6)

    def test_Fetchone(self):
        self.cu.execute("select name from test")
        row = self.cu.fetchone()
        self.assertEqual(row[0], "foo")
        row = self.cu.fetchone()
        self.assertEqual(row, None)

    def test_FetchoneNoStatement(self):
        cur = self.cx.cursor()
        row = cur.fetchone()
        self.assertEqual(row, None)

    def test_ArraySize(self):
        # must default ot 1
        self.assertEqual(self.cu.arraysize, 1)

        # now set to 2
        self.cu.arraysize = 2

        # now make the query return 3 rows
        self.cu.execute("delete from test")
        self.cu.execute("insert into test(name) values ('A')")
        self.cu.execute("insert into test(name) values ('B')")
        self.cu.execute("insert into test(name) values ('C')")
        self.cu.execute("select name from test")
        res = self.cu.fetchmany()

        self.assertEqual(len(res), 2)

    def test_Fetchmany(self):
        self.cu.execute("select name from test")
        res = self.cu.fetchmany(100)
        self.assertEqual(len(res), 1)
        res = self.cu.fetchmany(100)
        self.assertEqual(res, [])

    def test_FetchmanyKwArg(self):
        """Checks if fetchmany works with keyword arguments"""
        self.cu.execute("select name from test")
        res = self.cu.fetchmany(size=100)
        self.assertEqual(len(res), 1)

    def test_Fetchall(self):
        self.cu.execute("select name from test")
        res = self.cu.fetchall()
        self.assertEqual(len(res), 1)
        res = self.cu.fetchall()
        self.assertEqual(res, [])

    def test_Setinputsizes(self):
        self.cu.setinputsizes([3, 4, 5])

    def test_Setoutputsize(self):
        self.cu.setoutputsize(5, 0)

    def test_SetoutputsizeNoColumn(self):
        self.cu.setoutputsize(42)

    def test_CursorConnection(self):
        # Optional DB-API extension.
        self.assertEqual(self.cu.connection, self.cx)

    def test_WrongCursorCallable(self):
        with self.assertRaises(TypeError):
            def f(): pass

            cur = self.cx.cursor(f)

    def test_CursorWrongClass(self):
        class Foo: pass

        foo = Foo()
        with self.assertRaises(TypeError):
            cur = monetdbe.Cursor(foo)

    @unittest.skip("TODO: (gijs) this crashes monetdb")
    def test_LastRowIDOnReplace(self):
        """
        INSERT OR REPLACE and REPLACE INTO should produce the same behavior.
        """
        sql = '{} INTO test(id, unique_test) VALUES (?, ?)'
        for statement in ('INSERT OR REPLACE', 'REPLACE'):
            with self.subTest(statement=statement):
                self.cu.execute(sql.format(statement), (1, 'foo'))
                self.assertEqual(self.cu.lastrowid, 1)

    def test_LastRowIDOnIgnore(self):
        self.cu.execute(
            "insert or ignore into test(unique_test) values (?)",
            ('test',))
        self.assertEqual(self.cu.lastrowid, 2)
        self.cu.execute(
            "insert or ignore into test(unique_test) values (?)",
            ('test',))
        self.assertEqual(self.cu.lastrowid, 2)

    @unittest.skip("TODO: (gijs) this crashes monetdb")
    def test_LastRowIDInsertOR(self):
        results = []
        for statement in ('FAIL', 'ABORT', 'ROLLBACK'):
            sql = 'INSERT OR {} INTO test(unique_test) VALUES (?)'
            with self.subTest(statement='INSERT OR {}'.format(statement)):
                formatted = sql.format(statement)
                self.cu.execute(formatted, (statement,))
                results.append((statement, self.cu.lastrowid))
                with self.assertRaises(monetdbe.IntegrityError):
                    self.cu.execute(sql.format(statement), (statement,))
                results.append((statement, self.cu.lastrowid))
        expected = [
            ('FAIL', 2), ('FAIL', 2),
            ('ABORT', 3), ('ABORT', 3),
            ('ROLLBACK', 4), ('ROLLBACK', 4),
        ]
        self.assertEqual(results, expected)


class ThreadTests(unittest.TestCase):
    def setUp(self):
        self.con = monetdbe.connect(":memory:")
        self.cur = self.con.cursor()
        # NOTE: (gijs) replaced binary type with blob
        self.cur.execute("create table test(id integer primary key, name text, bin blob, ratio float, ts timestamp)")

    def tearDown(self):
        self.cur.close()
        self.con.close()

    def test_ConCursor(self):
        def run(con, errors):
            try:
                cur = con.cursor()
                errors.append("did not raise ProgrammingError")
                return
            except monetdbe.ProgrammingError:
                return
            except:
                errors.append("raised wrong exception")

        errors = []
        t = threading.Thread(target=run, kwargs={"con": self.con, "errors": errors})
        t.start()
        t.join()
        if len(errors) > 0:
            self.fail("\n".join(errors))

    def test_ConCommit(self):
        def run(con, errors):
            try:
                con.commit()
                errors.append("did not raise ProgrammingError")
                return
            except monetdbe.ProgrammingError:
                return
            except:
                errors.append("raised wrong exception")

        errors = []
        t = threading.Thread(target=run, kwargs={"con": self.con, "errors": errors})
        t.start()
        t.join()
        if len(errors) > 0:
            self.fail("\n".join(errors))

    def test_ConRollback(self):
        def run(con, errors):
            try:
                con.rollback()
                errors.append("did not raise ProgrammingError")
                return
            except monetdbe.ProgrammingError:
                return
            except:
                errors.append("raised wrong exception")

        errors = []
        t = threading.Thread(target=run, kwargs={"con": self.con, "errors": errors})
        t.start()
        t.join()
        if len(errors) > 0:
            self.fail("\n".join(errors))

    def test_ConClose(self):
        def run(con, errors):
            try:
                con.close()
                errors.append("did not raise ProgrammingError")
                return
            except monetdbe.ProgrammingError:
                return
            except:
                errors.append("raised wrong exception")

        errors = []
        t = threading.Thread(target=run, kwargs={"con": self.con, "errors": errors})
        t.start()
        t.join()
        if len(errors) > 0:
            self.fail("\n".join(errors))

    def test_CurImplicitBegin(self):
        def run(cur, errors):
            try:
                cur.execute("insert into test(name) values ('a')")
                errors.append("did not raise ProgrammingError")
                return
            except monetdbe.ProgrammingError:
                return
            except:
                errors.append("raised wrong exception")

        errors = []
        t = threading.Thread(target=run, kwargs={"cur": self.cur, "errors": errors})
        t.start()
        t.join()
        if len(errors) > 0:
            self.fail("\n".join(errors))

    def test_CurClose(self):
        def run(cur, errors):
            try:
                cur.close()
                errors.append("did not raise ProgrammingError")
                return
            except monetdbe.ProgrammingError:
                return
            except:
                errors.append("raised wrong exception")

        errors = []
        t = threading.Thread(target=run, kwargs={"cur": self.cur, "errors": errors})
        t.start()
        t.join()
        if len(errors) > 0:
            self.fail("\n".join(errors))

    def test_CurExecute(self):
        def run(cur, errors):
            try:
                cur.execute("select name from test")
                errors.append("did not raise ProgrammingError")
                return
            except monetdbe.ProgrammingError:
                return
            except:
                errors.append("raised wrong exception")

        errors = []
        self.cur.execute("insert into test(name) values ('a')")
        t = threading.Thread(target=run, kwargs={"cur": self.cur, "errors": errors})
        t.start()
        t.join()
        if len(errors) > 0:
            self.fail("\n".join(errors))

    def test_CurIterNext(self):
        def run(cur, errors):
            try:
                row = cur.fetchone()
                errors.append("did not raise ProgrammingError")
                return
            except monetdbe.ProgrammingError:
                return
            except:
                errors.append("raised wrong exception")

        errors = []
        self.cur.execute("insert into test(name) values ('a')")
        self.cur.execute("select name from test")
        t = threading.Thread(target=run, kwargs={"cur": self.cur, "errors": errors})
        t.start()
        t.join()
        if len(errors) > 0:
            self.fail("\n".join(errors))


class ConstructorTests(unittest.TestCase):
    def test_Date(self):
        d = monetdbe.Date(2004, 10, 28)

    def test_Time(self):
        t = monetdbe.Time(12, 39, 35)

    def test_Timestamp(self):
        ts = monetdbe.Timestamp(2004, 10, 28, 12, 39, 35)

    def test_DateFromTicks(self):
        d = monetdbe.DateFromTicks(42)

    def test_TimeFromTicks(self):
        t = monetdbe.TimeFromTicks(42)

    def test_TimestampFromTicks(self):
        ts = monetdbe.TimestampFromTicks(42)

    def test_Binary(self):
        b = monetdbe.Binary(b"\0'")


class ExtensionTests(unittest.TestCase):
    def test_ScriptStringSql(self):
        con = monetdbe.connect(":memory:")
        cur = con.cursor()
        cur.executescript("""
            -- bla bla
            /* a stupid comment */
            create table a(i int);
            insert into a(i) values (5);
            """)
        cur.execute("select i from a")
        res = cur.fetchone()[0]
        self.assertEqual(res, 5)

    def test_ScriptSyntaxError(self):
        con = monetdbe.connect(":memory:")
        cur = con.cursor()
        with self.assertRaises(monetdbe.OperationalError):
            cur.executescript("create table test(x); asdf; create table test2(x)")

    def test_ScriptErrorNormal(self):
        con = monetdbe.connect(":memory:")
        cur = con.cursor()
        with self.assertRaises(monetdbe.OperationalError):
            cur.executescript("create table test(sadfsadfdsa); select foo from hurz;")

    def test_CursorExecutescriptAsBytes(self):
        con = monetdbe.connect(":memory:")
        cur = con.cursor()
        with self.assertRaises(ValueError) as cm:
            cur.executescript(b"create table test(foo); insert into test(foo) values (5);")
        self.assertEqual(str(cm.exception), 'script argument must be unicode.')

    def test_ConnectionExecute(self):
        con = monetdbe.connect(":memory:")
        result = con.execute("select 5").fetchone()[0]
        self.assertEqual(result, 5, "Basic test of Connection.execute")

    def test_ConnectionExecutemany(self):
        con = monetdbe.connect(":memory:")
        # NOTE: (gijs) added type int, required for MonetDB
        con.execute("create table test(foo int)")
        con.executemany("insert into test(foo) values (?)", [(3,), (4,)])
        result = con.execute("select foo from test order by foo").fetchall()
        self.assertEqual(result[0][0], 3, "Basic test of Connection.executemany")
        self.assertEqual(result[1][0], 4, "Basic test of Connection.executemany")

    def test_ConnectionExecutescript(self):
        con = monetdbe.connect(":memory:")
        # NOTE: (gijs) added type int, required for MonetDB
        con.executescript("create table test(foo int); insert into test(foo) values (5);")
        result = con.execute("select foo from test").fetchone()[0]
        self.assertEqual(result, 5, "Basic test of Connection.executescript")


class ClosedConTests(unittest.TestCase):
    def test_ClosedConCursor(self):
        con = monetdbe.connect(":memory:")
        con.close()
        with self.assertRaises(monetdbe.ProgrammingError):
            cur = con.cursor()

    def test_ClosedConCommit(self):
        con = monetdbe.connect(":memory:")
        con.close()
        with self.assertRaises(monetdbe.ProgrammingError):
            con.commit()

    def test_ClosedConRollback(self):
        con = monetdbe.connect(":memory:")
        con.close()
        with self.assertRaises(monetdbe.ProgrammingError):
            con.rollback()

    def test_ClosedCurExecute(self):
        con = monetdbe.connect(":memory:")
        cur = con.cursor()
        con.close()
        with self.assertRaises(monetdbe.ProgrammingError):
            cur.execute("select 4")

    def test_ClosedCreateFunction(self):
        con = monetdbe.connect(":memory:")
        con.close()

        def f(x): return 17

        with self.assertRaises(monetdbe.ProgrammingError):
            con.create_function("foo", 1, f)

    def test_ClosedCreateAggregate(self):
        con = monetdbe.connect(":memory:")
        con.close()

        class Agg:
            def __init__(self):
                pass

            def step(self, x):
                pass

            def finalize(self):
                return 17

        with self.assertRaises(monetdbe.ProgrammingError):
            con.create_aggregate("foo", 1, Agg)

    def test_ClosedSetAuthorizer(self):
        con = monetdbe.connect(":memory:")
        con.close()

        def authorizer(*args):
            return monetdbe.DENY

        with self.assertRaises(monetdbe.ProgrammingError):
            con.set_authorizer(authorizer)

    def test_ClosedSetProgressCallback(self):
        con = monetdbe.connect(":memory:")
        con.close()

        def progress(): pass

        with self.assertRaises(monetdbe.ProgrammingError):
            con.set_progress_handler(progress, 100)

    def test_ClosedCall(self):
        con = monetdbe.connect(":memory:")
        con.close()
        with self.assertRaises(monetdbe.ProgrammingError):
            con()


class ClosedCurTests(unittest.TestCase):
    def test_Closed(self):
        con = monetdbe.connect(":memory:")
        cur = con.cursor()
        cur.close()

        for method_name in ("execute", "executemany", "executescript", "fetchall", "fetchmany", "fetchone"):
            if method_name in ("execute", "executescript"):
                params = ("select 4 union select 5",)
            elif method_name == "executemany":
                params = ("insert into foo(bar) values (?)", [(3,), (4,)])
            else:
                params = []

            with self.assertRaises(monetdbe.ProgrammingError):
                method = getattr(cur, method_name)
                method(*params)


class monetdbeOnConflictTests(unittest.TestCase):
    """
    Tests for monetdbe's "insert on conflict" feature.

    See https://www.monetdbe.org/lang_conflict.html for details.
    """

    def setUp(self):
        self.cx = monetdbe.connect(":memory:")
        self.cu = self.cx.cursor()
        self.cu.execute("""
          CREATE TABLE test(
            id INTEGER PRIMARY KEY auto_increment, name TEXT, unique_name TEXT UNIQUE
          );
        """)  # NOTE: (gijs) add auto_increment

    def tearDown(self):
        self.cu.close()
        self.cx.close()

    def test_OnConflictRollbackWithExplicitTransaction(self):
        self.cx.isolation_level = None  # autocommit mode
        self.cu = self.cx.cursor()
        # Start an explicit transaction.
        self.cu.execute("BEGIN")
        self.cu.execute("INSERT INTO test(name) VALUES ('abort_test')")
        self.cu.execute("INSERT OR ROLLBACK INTO test(unique_name) VALUES ('foo')")
        with self.assertRaises(monetdbe.IntegrityError):
            self.cu.execute("INSERT OR ROLLBACK INTO test(unique_name) VALUES ('foo')")
        # Use connection to commit.
        self.cx.commit()
        self.cu.execute("SELECT name, unique_name from test")
        # Transaction should have rolled back and nothing should be in table.
        self.assertEqual(self.cu.fetchall(), [])

    def test_OnConflictAbortRaisesWithExplicitTransactions(self):
        # Abort cancels the current sql statement but doesn't change anything
        # about the current transaction.
        self.cx.isolation_level = None  # autocommit mode
        self.cu = self.cx.cursor()
        # Start an explicit transaction.
        self.cu.execute("BEGIN TRANSACTION")  # NOTE: (gijs) added TRANSACTION
        self.cu.execute("INSERT INTO test(name) VALUES ('abort_test')")
        self.cu.execute("INSERT OR ABORT INTO test(unique_name) VALUES ('foo')")
        with self.assertRaises(monetdbe.IntegrityError):
            self.cu.execute("INSERT OR ABORT INTO test(unique_name) VALUES ('foo')")
        self.cx.commit()
        self.cu.execute("SELECT name, unique_name FROM test")
        # Expect the first two inserts to work, third to do nothing.
        self.assertEqual(self.cu.fetchall(), [('abort_test', None), (None, 'foo',)])

    def test_OnConflictRollbackWithoutTransaction(self):
        # Start of implicit transaction
        self.cu.execute("INSERT INTO test(name) VALUES ('abort_test')")
        self.cu.execute("INSERT OR ROLLBACK INTO test(unique_name) VALUES ('foo')")
        with self.assertRaises(monetdbe.IntegrityError):
            self.cu.execute("INSERT OR ROLLBACK INTO test(unique_name) VALUES ('foo')")
        self.cu.execute("SELECT name, unique_name FROM test")
        # Implicit transaction is rolled back on error.
        self.assertEqual(self.cu.fetchall(), [])

    def test_OnConflictAbortRaisesWithoutTransactions(self):
        # Abort cancels the current sql statement but doesn't change anything
        # about the current transaction.
        self.cu.execute("INSERT INTO test(name) VALUES ('abort_test')")
        self.cu.execute("INSERT OR ABORT INTO test(unique_name) VALUES ('foo')")
        with self.assertRaises(monetdbe.IntegrityError):
            self.cu.execute("INSERT OR ABORT INTO test(unique_name) VALUES ('foo')")
        # Make sure all other values were inserted.
        self.cu.execute("SELECT name, unique_name FROM test")
        self.assertEqual(self.cu.fetchall(), [('abort_test', None), (None, 'foo',)])

    def test_OnConflictFail(self):
        self.cu.execute("INSERT OR FAIL INTO test(unique_name) VALUES ('foo')")
        with self.assertRaises(monetdbe.IntegrityError):
            self.cu.execute("INSERT OR FAIL INTO test(unique_name) VALUES ('foo')")
        self.assertEqual(self.cu.fetchall(), [])

    def test_OnConflictIgnore(self):
        self.cu.execute("INSERT OR IGNORE INTO test(unique_name) VALUES ('foo')")
        # Nothing should happen.
        self.cu.execute("INSERT OR IGNORE INTO test(unique_name) VALUES ('foo')")
        self.cu.execute("SELECT unique_name FROM test")
        self.assertEqual(self.cu.fetchall(), [('foo',)])

    def test_OnConflictReplace(self):
        self.cu.execute("INSERT OR REPLACE INTO test(name, unique_name) VALUES ('Data!', 'foo')")
        # There shouldn't be an IntegrityError exception.
        self.cu.execute("INSERT OR REPLACE INTO test(name, unique_name) VALUES ('Very different data!', 'foo')")
        self.cu.execute("SELECT name, unique_name FROM test")
        self.assertEqual(self.cu.fetchall(), [('Very different data!', 'foo')])


def suite():
    module_suite = unittest.makeSuite(ModuleTests, "Check")
    connection_suite = unittest.makeSuite(ConnectionTests, "Check")
    cursor_suite = unittest.makeSuite(CursorTests, "Check")
    thread_suite = unittest.makeSuite(ThreadTests, "Check")
    constructor_suite = unittest.makeSuite(ConstructorTests, "Check")
    ext_suite = unittest.makeSuite(ExtensionTests, "Check")
    closed_con_suite = unittest.makeSuite(ClosedConTests, "Check")
    closed_cur_suite = unittest.makeSuite(ClosedCurTests, "Check")
    on_conflict_suite = unittest.makeSuite(monetdbeOnConflictTests, "Check")
    return unittest.TestSuite((
        module_suite, connection_suite, cursor_suite, thread_suite,
        constructor_suite, ext_suite, closed_con_suite, closed_cur_suite,
        on_conflict_suite,
    ))


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == "__main__":
    test()
