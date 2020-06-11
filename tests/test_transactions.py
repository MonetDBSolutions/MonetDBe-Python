# -*- coding: iso-8859-1 -*-
# monetdbe/test/transactions.py: tests transactions
#
# Copyright (C) 2005-2007 Gerhard Häring <gh@ghaering.de>
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

import os
import unittest
from tempfile import TemporaryDirectory

import monetdbe as monetdbe


class TransactionTests(unittest.TestCase):
    def setUp(self):
        self.db_path = TemporaryDirectory().name

        try:
            os.remove(self.db_path)
        except OSError:
            pass

        self.con1 = monetdbe.connect(self.db_path, timeout=0.1)
        self.cur1 = self.con1.cursor()

        self.con2 = monetdbe.connect(self.db_path, timeout=0.1)
        self.cur2 = self.con2.cursor()

    def tearDown(self):
        self.cur1.close()
        self.con1.close()

        self.cur2.close()
        self.con2.close()

        try:
            os.unlink(self.db_path)
        except OSError:
            pass

    def test_DMLDoesNotAutoCommitBefore(self):
        self.cur1.execute("create table test(i int)")
        self.cur1.execute("insert into test(i) values (5)")
        self.cur1.execute("create table test2(j int)")
        self.cur2.execute("select i from test")
        res = self.cur2.fetchall()
        self.assertEqual(len(res), 0)

    def test_InsertStartsTransaction(self):
        self.cur1.execute("create table test(i int)")
        self.cur1.execute("insert into test(i) values (5)")
        self.cur2.execute("select i from test")
        res = self.cur2.fetchall()
        self.assertEqual(len(res), 0)

    def test_UpdateStartsTransaction(self):
        self.cur1.execute("create table test(i int)")
        self.cur1.execute("insert into test(i) values (5)")
        self.con1.commit()
        self.cur1.execute("update test set i=6")
        self.cur2.execute("select i from test")
        res = self.cur2.fetchone()[0]
        self.assertEqual(res, 5)

    def test_DeleteStartsTransaction(self):
        self.cur1.execute("create table test(i int)")
        self.cur1.execute("insert into test(i) values (5)")
        self.con1.commit()
        self.cur1.execute("delete from test")
        self.cur2.execute("select i from test")
        res = self.cur2.fetchall()
        self.assertEqual(len(res), 1)

    def test_ReplaceStartsTransaction(self):
        self.cur1.execute("create table test(i int)")
        self.cur1.execute("insert into test(i) values (5)")
        self.con1.commit()
        self.cur1.execute("replace into test(i) values (6)")
        self.cur2.execute("select i from test")
        res = self.cur2.fetchall()
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][0], 5)

    def test_ToggleAutoCommit(self):
        self.cur1.execute("create table test(i int)")
        self.cur1.execute("insert into test(i) values (5)")
        self.con1.isolation_level = None
        self.assertEqual(self.con1.isolation_level, None)
        self.cur2.execute("select i from test")
        res = self.cur2.fetchall()
        self.assertEqual(len(res), 1)

        self.con1.isolation_level = "DEFERRED"
        self.assertEqual(self.con1.isolation_level, "DEFERRED")
        self.cur1.execute("insert into test(i) values (5)")
        self.cur2.execute("select i from test")
        res = self.cur2.fetchall()
        self.assertEqual(len(res), 1)

    @unittest.skipIf(monetdbe.monetdbe_version_info < (3, 2, 2),
                     'test hangs on monetdbe versions older than 3.2.2')
    def test_RaiseTimeout(self):
        self.cur1.execute("create table test(i int)")
        self.cur1.execute("insert into test(i) values (5)")
        with self.assertRaises(monetdbe.OperationalError):
            self.cur2.execute("insert into test(i) values (5)")

    @unittest.skipIf(monetdbe.monetdbe_version_info < (3, 2, 2),
                     'test hangs on monetdbe versions older than 3.2.2')
    def test_Locking(self):
        """
        This tests the improved concurrency with pymonetdbe 2.3.4. You needed
        to roll back con2 before you could commit con1.
        """
        self.cur1.execute("create table test(i int)")
        self.cur1.execute("insert into test(i) values (5)")
        with self.assertRaises(monetdbe.OperationalError):
            self.cur2.execute("insert into test(i) values (5)")
        # NO self.con2.rollback() HERE!!!
        self.con1.commit()

    def test_RollbackCursorConsistency(self):
        """
        Checks if cursors on the connection are set into a "reset" state
        when a rollback is done on the connection.
        """
        con = monetdbe.connect(":memory:")
        cur = con.cursor()
        cur.execute("create table test(x)")
        cur.execute("insert into test(x) values (5)")
        cur.execute("select 1 union select 2 union select 3")

        con.rollback()
        with self.assertRaises(monetdbe.InterfaceError):
            cur.fetchall()


class SpecialCommandTests(unittest.TestCase):
    def setUp(self):
        self.con = monetdbe.connect(":memory:")
        self.cur = self.con.cursor()

    def test_DropTable(self):
        # note (gijs): added int type
        self.cur.execute("create table test(i int)")
        self.cur.execute("insert into test(i) values (5)")
        self.cur.execute("drop table test")

    def test_Pragma(self):
        # note (gijs): added int type
        self.cur.execute("create table test(i int)")
        self.cur.execute("insert into test(i) values (5)")
        self.cur.execute("pragma count_changes=1")

    def tearDown(self):
        self.cur.close()
        self.con.close()


class TransactionalDDL(unittest.TestCase):
    def setUp(self):
        self.con = monetdbe.connect(":memory:")

    def test_DdlDoesNotAutostartTransaction(self):
        # For backwards compatibility reasons, DDL statements should not
        # implicitly start a transaction.
        self.con.execute("create table test(i int)")
        self.con.rollback()
        result = self.con.execute("select * from test").fetchall()
        self.assertEqual(result, [])

    def test_ImmediateTransactionalDDL(self):
        # You can achieve transactional DDL by issuing a BEGIN
        # statement manually.
        self.con.execute("begin immediate")
        self.con.execute("create table test(i int)")
        self.con.rollback()
        with self.assertRaises(monetdbe.OperationalError):
            self.con.execute("select * from test")

    def test_TransactionalDDL(self):
        # You can achieve transactional DDL by issuing a BEGIN
        # statement manually.
        self.con.execute("begin")
        self.con.execute("create table test(i int)")
        self.con.rollback()
        with self.assertRaises(monetdbe.OperationalError):
            self.con.execute("select * from test")

    def tearDown(self):
        self.con.close()


def suite():
    default_suite = unittest.makeSuite(TransactionTests, "Check")
    special_command_suite = unittest.makeSuite(SpecialCommandTests, "Check")
    ddl_suite = unittest.makeSuite(TransactionalDDL, "Check")
    return unittest.TestSuite((default_suite, special_command_suite, ddl_suite))


def test():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == "__main__":
    test()
