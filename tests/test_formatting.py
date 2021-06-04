import unittest

import monetdbe as monetdbe


class TransactionTests(unittest.TestCase):
    def setUp(self):
        self.con = monetdbe.connect()
        self.con.execute("create table test(i int, s text)")

    def tearDown(self):
        self.con.close()

    def test_vanilla(self):
        """This should just work"""
        self.con.execute("insert into test(i, s) values (5, '?%:%(bla)')")

    def test_qmark(self):
        """Question mark style, e.g. ...WHERE name=?"""
        self.con.execute("insert into test(i, s) values (?, ?)", (5, "?%:%(bla)"))

    def test_numeric(self):
        """Numeric, positional style, e.g. ...WHERE name=:1"""
        self.con.execute("insert into test(i, s) values (:1, :2)", (5, "?%:%(bla)"), paramstyle="numeric")

    def test_named(self):
        """Named style, e.g. ...WHERE name=:name"""
        self.con.execute("insert into test(i, s) values (:int, :str)", {'int': 5, 'str': "?%:%(bla)"})

    def test_format(self):
        """ANSI C printf format codes, e.g. ...WHERE name=%s"""
        self.con.execute("insert into test(i, s) values (%s, %s)", (5, "?%:%(bla)"), paramstyle="format")

    def test_pyformat(self):
        """Python extended format codes, e.g. ...WHERE name=%(name)s"""
        self.con.execute("insert into test(i, s) values (%(name)s, %(str)s)", {'name': 5, 'str': "?%:%(bla)"},
                         paramstyle="pyformat")

    def test_wrongparamstyle(self):
        with self.assertRaises(ValueError):
            self.con.execute("insert into test(i, s) values (%(name)s, %(str)s)", {'name': 5, 'str': "?%:%(bla)"},
                             paramstyle="wrong")

    def test_should_fail(self):
        """parameters must be sequence or mapping"""
        with self.assertRaises(ValueError):
            self.con.execute("insert into test(i, s) values (?)", 5)

    @unittest.skip("we don't support multiple open connections yet")
    def test_qmark_multiple_cons(self):
        con1 = monetdbe.connect()
        con1.execute("create table test(i int, s text)")
        con1.execute("insert into test(i, s) values (?, ?)", (5, "bla"))
        con2 = monetdbe.connect()
        con2.execute("create table test(i int, s text)")
        con2.execute("insert into test(i, s) values (?, ?)", (5, "bla"))
        con1.execute("create table test(i int, s text)")
        con1.execute("insert into test(i, s) values (?, ?)", (5, "bla"))
