# -*- coding: iso-8859-1 -*-
# monetdbe/test/types.py: tests for type conversion and detection
#
# Copyright (C) 2005 Gerhard H�ring <gh@ghaering.de>
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
import datetime
import unittest
import zlib

import monetdbe as monetdbe


class monetdbeTypeTests(unittest.TestCase):
    def setUp(self):
        self.con = monetdbe.connect(":memory:")
        self.cur = self.con.cursor()
        self.cur.execute("create table test(i BIGINT, s text, f float, b blob)")

    def tearDown(self):
        self.cur.close()
        self.con.close()

    def test_String(self):
        self.cur.execute("insert into test(s) values (?)", ("�sterreich",))
        self.cur.execute("select s from test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], "�sterreich")

    def test_SmallInt(self):
        self.cur.execute("insert into test(i) values (?)", (42,))
        self.cur.execute("select i from test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], 42)

    def test_LargeInt(self):
        num = 2 ** 40
        self.cur.execute("insert into test(i) values (?)", (num,))
        self.cur.execute("select i from test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], num)

    def test_Float(self):
        val = 3.14
        self.cur.execute("insert into test(f) values (?)", (val,))
        self.cur.execute("select f from test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], val)

    def test_Blob(self):
        sample = b"Guglhupf"
        val = memoryview(sample)
        self.cur.execute("insert into test(b) values (?)", (val,))
        self.cur.execute("select b from test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], sample)

    def test_UnicodeExecute(self):
        self.cur.execute("select '�sterreich'")
        row = self.cur.fetchone()
        self.assertEqual(row[0], "�sterreich")


@unittest.skip("todo: implement, see issue #56")
class DeclTypesTests(unittest.TestCase):
    class Foo:
        def __init__(self, _val):
            if isinstance(_val, bytes):
                # monetdbe always calls __init__ with a bytes created from a
                # UTF-8 string when __conform__ was used to store the object.
                _val = _val.decode('utf-8')
            self.val = _val

        def __eq__(self, other):
            if not isinstance(other, DeclTypesTests.Foo):
                return NotImplemented
            return self.val == other.val

        def __conform__(self, protocol):
            if protocol is monetdbe.PrepareProtocol:
                return self.val
            else:
                return None

        def __str__(self):
            return "<%s>" % self.val

    class BadConform:
        def __init__(self, exc):
            self.exc = exc

        def __conform__(self, protocol):
            raise self.exc

    def setUp(self):
        self.con = monetdbe.connect(":memory:", detect_types=monetdbe.PARSE_DECLTYPES)
        self.cur = self.con.cursor()
        self.cur.execute(
            # note (gijs) modifed the types here
            "create table test(i bigint, s string, f float, b bool, u string, foo string, bin blob, n1 NUMERIC, n2 NUMERIC(5), bad blob)")
        # "create table test(i int, s str, f float, b bool, u unicode, foo foo, bin blob, n1 number, n2 number(5), bad bad)")

        # override float, make them always return the same number
        monetdbe.converters["FLOAT"] = lambda x: 47.2

        # and implement two custom ones
        monetdbe.converters["BOOL"] = lambda x: bool(int(x))
        monetdbe.converters["FOO"] = DeclTypesTests.Foo
        monetdbe.converters["BAD"] = DeclTypesTests.BadConform
        monetdbe.converters["WRONG"] = lambda x: "WRONG"
        monetdbe.converters["NUMBER"] = float

    def tearDown(self):
        del monetdbe.converters["FLOAT"]
        del monetdbe.converters["BOOL"]
        del monetdbe.converters["FOO"]
        del monetdbe.converters["BAD"]
        del monetdbe.converters["WRONG"]
        del monetdbe.converters["NUMBER"]
        self.cur.close()
        self.con.close()

    def test_String(self):
        # default
        self.cur.execute("insert into test(s) values (?)", ("foo",))
        self.cur.execute('select s as "s [WRONG]" from test')
        row = self.cur.fetchone()
        self.assertEqual(row[0], "foo")

    def test_SmallInt(self):
        # default
        self.cur.execute("insert into test(i) values (?)", (42,))
        self.cur.execute("select i from test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], 42)

    def test_LargeInt(self):
        # default
        num = 2 ** 40
        self.cur.execute("insert into test(i) values (?)", (num,))
        self.cur.execute("select i from test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], num)

    def test_Float(self):
        # custom
        val = 3.14
        self.cur.execute("insert into test(f) values (?)", (val,))
        self.cur.execute("select f from test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], 47.2)

    def test_Bool(self):
        # custom
        self.cur.execute("insert into test(b) values (?)", (False,))
        self.cur.execute("select b from test")
        row = self.cur.fetchone()
        self.assertIs(row[0], False)

        self.cur.execute("delete from test")
        self.cur.execute("insert into test(b) values (?)", (True,))
        self.cur.execute("select b from test")
        row = self.cur.fetchone()
        self.assertIs(row[0], True)

    def test_Unicode(self):
        # default
        val = "\xd6sterreich"
        self.cur.execute("insert into test(u) values (?)", (val,))
        self.cur.execute("select u from test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], val)

    @unittest.skip("we don't support custom types for now")
    def test_Foo(self):
        val = DeclTypesTests.Foo("bla")
        self.cur.execute("insert into test(foo) values (?)", (val,))
        self.cur.execute("select foo from test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], val)

    def test_ErrorInConform(self):
        val = DeclTypesTests.BadConform(TypeError)
        with self.assertRaises(monetdbe.InterfaceError):
            self.cur.execute("insert into test(bad) values (?)", (val,))
        with self.assertRaises(monetdbe.InterfaceError):
            self.cur.execute("insert into test(bad) values (:val)", {"val": val})

        val = DeclTypesTests.BadConform(KeyboardInterrupt)
        with self.assertRaises(KeyboardInterrupt):
            self.cur.execute("insert into test(bad) values (?)", (val,))
        with self.assertRaises(KeyboardInterrupt):
            self.cur.execute("insert into test(bad) values (:val)", {"val": val})

    def test_UnsupportedSeq(self):
        class Bar:
            pass

        val = Bar()
        with self.assertRaises(monetdbe.InterfaceError):
            self.cur.execute("insert into test(f) values (?)", (val,))

    def test_UnsupportedDict(self):
        class Bar:
            pass

        val = Bar()
        with self.assertRaises(monetdbe.InterfaceError):
            self.cur.execute("insert into test(f) values (:val)", {"val": val})

    def test_Blob(self):
        # default
        sample = b"Guglhupf"
        val = memoryview(sample)
        self.cur.execute("insert into test(bin) values (?)", (val,))
        self.cur.execute("select bin from test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], sample)

    def test_Number1(self):
        self.cur.execute("insert into test(n1) values (5)")
        value = self.cur.execute("select n1 from test").fetchone()[0]
        # if the converter is not used, it's an int instead of a float
        self.assertEqual(type(value), float)

    def test_Number2(self):
        """Checks whether converter names are cut off at '(' characters"""
        self.cur.execute("insert into test(n2) values (5)")
        value = self.cur.execute("select n2 from test").fetchone()[0]
        # if the converter is not used, it's an int instead of a float
        self.assertEqual(type(value), float)


@unittest.skip("todo: implement, see issue #56")
class ColNamesTests(unittest.TestCase):
    def setUp(self):
        self.con = monetdbe.connect(":memory:", detect_types=monetdbe.PARSE_COLNAMES)
        self.cur = self.con.cursor()

        # note (gijs) changed this to type string
        self.cur.execute("create table test(x string)")
        # self.cur.execute("create table test(x foo)")

        monetdbe.converters["FOO"] = lambda x: "[%s]" % x.decode("ascii")
        monetdbe.converters["BAR"] = lambda x: "<%s>" % x.decode("ascii")
        monetdbe.converters["EXC"] = lambda x: 5 / 0
        monetdbe.converters["B1B1"] = lambda x: "MARKER"

    def tearDown(self):
        del monetdbe.converters["FOO"]
        del monetdbe.converters["BAR"]
        del monetdbe.converters["EXC"]
        del monetdbe.converters["B1B1"]
        self.cur.close()
        self.con.close()

    def test_DeclTypeNotUsed(self):
        """
        Assures that the declared type is not used when PARSE_DECLTYPES
        is not set.
        """
        self.cur.execute("insert into test(x) values (?)", ("xxx",))
        self.cur.execute("select x from test")
        val = self.cur.fetchone()[0]
        self.assertEqual(val, "xxx")

    def test_None(self):
        self.cur.execute("insert into test(x) values (?)", (None,))
        self.cur.execute("select x from test")
        val = self.cur.fetchone()[0]
        self.assertEqual(val, None)

    def test_ColName(self):
        self.cur.execute("insert into test(x) values (?)", ("xxx",))
        self.cur.execute('select x as "x y [bar]" from test')
        val = self.cur.fetchone()[0]
        self.assertEqual(val, "<xxx>")

        # Check if the stripping of colnames works. Everything after the first
        # '[' (and the preceeding space) should be stripped.
        self.assertEqual(self.cur.description[0][0], "x y")

    def test_CaseInConverterName(self):
        self.cur.execute("select 'other' as \"x [b1b1]\"")
        val = self.cur.fetchone()[0]
        self.assertEqual(val, "MARKER")

    def test_CursorDescriptionNoRow(self):
        """
        cursor.description should at least provide the column name(s), even if
        no row returned.
        """
        self.cur.execute("select * from test where 0 = 1")
        self.assertEqual(self.cur.description[0][0], "x")

    def test_CursorDescriptionInsert(self):
        self.cur.execute("insert into test values (1)")
        self.assertIsNone(self.cur.description)


class CommonTableExpressionTests(unittest.TestCase):

    def setUp(self):
        self.con = monetdbe.connect(":memory:")
        self.cur = self.con.cursor()
        self.cur.execute("create table test(x int)")

    def tearDown(self):
        self.cur.close()
        self.con.close()

    def test_CursorDescriptionCTESimple(self):
        self.cur.execute("with one as (select 1) select * from one")
        self.assertIsNotNone(self.cur.description)

    def test_CursorDescriptionCTESMultipleColumns(self):
        self.cur.execute("insert into test values(1)")
        self.cur.execute("insert into test values(2)")
        self.cur.execute("with testCTE as (select * from test) select * from testCTE")
        self.assertIsNotNone(self.cur.description)
        self.assertEqual(self.cur.description[0][0], "x")

    def test_CursorDescriptionCTE(self):
        self.cur.execute("insert into test values (1)")
        self.cur.execute("with bar as (select * from test) select * from test where x = 1")
        self.assertIsNotNone(self.cur.description)
        self.assertEqual(self.cur.description[0][0], "x")
        self.cur.execute("with bar as (select * from test) select * from test where x = 2")
        self.assertIsNotNone(self.cur.description)
        self.assertEqual(self.cur.description[0][0], "x")


@unittest.skip("todo: implement, see issue #57")
class ObjectAdaptationTests(unittest.TestCase):
    def cast(obj):
        return float(obj)

    cast = staticmethod(cast)  # type: ignore

    def setUp(self):
        self.con = monetdbe.connect(":memory:")
        try:
            del monetdbe.adapters[int]
        except Exception:
            pass
        monetdbe.register_adapter(int, ObjectAdaptationTests.cast)
        self.cur = self.con.cursor()

    def tearDown(self):
        del monetdbe.adapters[(int, monetdbe.PrepareProtocol)]
        self.cur.close()
        self.con.close()

    def test_CasterIsUsed(self):
        self.cur.execute("select ?", (4,))
        val = self.cur.fetchone()[0]
        self.assertEqual(type(val), float)


class BinaryConverterTests(unittest.TestCase):
    def convert(s):
        return zlib.decompress(s)

    convert = staticmethod(convert)  # type: ignore

    def setUp(self):
        self.con = monetdbe.connect(":memory:", detect_types=monetdbe.PARSE_COLNAMES)
        monetdbe.register_converter("bin", BinaryConverterTests.convert)

    def tearDown(self):
        self.con.close()

    @unittest.skip("note (gijs): skipping this test/functionality for now")
    def test_BinaryInputForConverter(self):
        testdata = b"abcdefg" * 10
        result = self.con.execute('select ? as "x [bin]"', (memoryview(zlib.compress(testdata)),)).fetchone()[0]
        self.assertEqual(testdata, result)


class DateTimeTests(unittest.TestCase):
    def setUp(self):
        self.con = monetdbe.connect(":memory:")  # , detect_types=monetdbe.PARSE_DECLTYPES)
        self.cur = self.con.cursor()
        self.cur.execute("create table test(d date, ts timestamp)")

    def tearDown(self):
        self.cur.close()
        self.con.close()

    def test_monetdbeDate(self):
        d = monetdbe.Date(2004, 2, 14)
        self.cur.execute("insert into test(d) values (?)", (d,))
        self.cur.execute("select d from test")
        d2 = self.cur.fetchone()[0]
        self.assertEqual(d, d2)

    def test_monetdbeTimestamp(self):
        ts = monetdbe.Timestamp(2004, 2, 14, 7, 15, 0)
        self.cur.execute("insert into test(ts) values (?)", (ts,))
        self.cur.execute("select ts from test")
        ts2 = self.cur.fetchone()[0]
        self.assertEqual(ts, ts2)

    def test_SqlTimestamp(self):
        now = datetime.datetime.utcnow()
        self.cur.execute("insert into test(ts) values (current_timestamp)")
        self.cur.execute("select ts from test")
        ts = self.cur.fetchone()[0]
        self.assertEqual(type(ts), datetime.datetime)
        self.assertEqual(ts.year, now.year)

    def test_DateTimeSubSeconds(self):
        ts = monetdbe.Timestamp(2004, 2, 14, 7, 15, 0, 500000)
        self.cur.execute("insert into test(ts) values (?)", (ts,))
        self.cur.execute("select ts from test")
        ts2 = self.cur.fetchone()[0]
        self.assertEqual(ts, ts2)

    @unittest.skip("note (gijs): we don't support microseconds, only ms")
    def test_DateTimeSubSecondsFloatingPoint(self):
        ts = monetdbe.Timestamp(2004, 2, 14, 7, 15, 0, 510241)
        self.cur.execute("insert into test(ts) values (?)", (ts,))
        self.cur.execute("select ts from test")
        ts2 = self.cur.fetchone()[0]
        self.assertEqual(ts, ts2)


@unittest.skip("todo: complex types not yet supported, see issue #58")
class monetdbeTypeComplexTests(unittest.TestCase):
    def setUp(self):
        self.con = monetdbe.connect(":memory:")
        self.cur = self.con.cursor()
        self.cur.execute("create table test(c complex)")

    def tearDown(self):
        self.cur.close()
        self.con.close()

    def test_complex(self):
        val = complex(10, 20)
        self.cur.execute("insert into test(c) values (?)", (val,))
        self.cur.execute("select c from test")
        row = self.cur.fetchone()
        self.assertEqual(row[0], val)
