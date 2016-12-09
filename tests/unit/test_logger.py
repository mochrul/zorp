#!/usr/bin/env python2.7

import unittest

from Zorp.Common import LogSpecItem

class TestLogSpecItem(unittest.TestCase):

    def test_valid_formats(self):
        valid_logspec_items = [
            "category1.category2:3",
            "category1.*:3",
            "*.category2:3",
            "*.*:3",
        ]

        for valid_logspec_item in valid_logspec_items:
            LogSpecItem(valid_logspec_item)

    def test_invalid_verbosity(self):
        with self.assertRaises(ValueError):
            LogSpecItem("c1.c2:11")

        with self.assertRaises(ValueError):
            LogSpecItem("c1.c2.c3:11")

        with self.assertRaises(ValueError):
            LogSpecItem(".c1:11")

        with self.assertRaises(ValueError):
            LogSpecItem("c1.:11")

    def test_verbosity_comparision(self):
        log_spec = LogSpecItem("a.b:3")
        self.assertTrue(log_spec.is_log_enabled("a.b", 2))
        self.assertTrue(log_spec.is_log_enabled("a.b", 3))
        self.assertFalse(log_spec.is_log_enabled("a.b", 4))

    def test_category_glob_match(self):
        self.assertTrue(LogSpecItem("*.b:3").is_log_enabled("a.b", 3))
        self.assertTrue(LogSpecItem("a.*:3").is_log_enabled("a.b", 3))
        self.assertTrue(LogSpecItem("*.*:3").is_log_enabled("a.b", 3))

        self.assertFalse(LogSpecItem("*.b:2").is_log_enabled("a.b", 3))
        self.assertFalse(LogSpecItem("a.*:2").is_log_enabled("a.b", 3))
        self.assertFalse(LogSpecItem("*.*:2").is_log_enabled("a.b", 3))

    def test_category_exact_match(self):
        self.assertTrue(LogSpecItem("a.b:3").is_log_enabled("a.b", 3))
        self.assertFalse(LogSpecItem("a.b:3").is_log_enabled("a.b", 4))
        self.assertFalse(LogSpecItem("aa.b:3").is_log_enabled("a.b", 3))
        self.assertFalse(LogSpecItem("a.b:3").is_log_enabled("aa.b", 3))
        self.assertFalse(LogSpecItem("a.bb:3").is_log_enabled("a.b", 3))
        self.assertFalse(LogSpecItem("a.b:3").is_log_enabled("a.bb", 3))


from Zorp.Common import LogFilter

class TestLogFilter(unittest.TestCase):

    def test_single_match(self):
        self.assertTrue(LogFilter(0, "a.b:4").is_log_enabled("a.b", 4))
        self.assertTrue(LogFilter(0, "c.d:3,a.b:4").is_log_enabled("a.b", 4))
        self.assertTrue(LogFilter(0, "a.b:4,c.d:3").is_log_enabled("a.b", 4))

    def test_multiple_match(self):
        self.assertTrue(LogFilter(0, "a.b:4,*.*:4").is_log_enabled("a.b", 4))

    def test_no_match(self):
        self.assertFalse(LogFilter(0, "a.b:3").is_log_enabled("a.b", 4))
        self.assertFalse(LogFilter(0, "a.b:3,c.d:3").is_log_enabled("a.b", 4))

    def test_fallback_to_verbisity(self):
        self.assertTrue(LogFilter(4, "").is_log_enabled("a.b", 4))
        self.assertTrue(LogFilter(4, "a.b:3").is_log_enabled("a.b", 4))
        self.assertTrue(LogFilter(4, "a.b:3,c.d:3").is_log_enabled("a.b", 4))


import os
from Zorp.Common import Logger

class TestLogger(unittest.TestCase):

    def setUp(self):
        import sys
        import StringIO

        self.stderr_str = StringIO.StringIO()
        sys.stderr = self.stderr_str
        self.logger = Logger()

    def test_log_format(self):
        self.assertEqual(self.logger.format_log("sessionid", "logclass", 3, "message"),
                         "None[0]: logclass(3): (sessionid): message")
        self.assertEqual(self.logger.format_log(None, "logclass", 3, "message"),
                         "None[0]: logclass(3): (nosession): message")
        self.assertEqual(self.logger.format_log(None, "logclass", 3, "%s %s", ("printf-style", "message")),
                         "None[0]: logclass(3): (nosession): printf-style message")

    def test_log(self):
        self.logger.init("test", use_syslog=False)

        self.logger.log("sessionid", "log.class", 3, "message")
        self.assertEqual(self.stderr_str.getvalue(),
                         "test[%d]: log.class(3): (sessionid): message\n" % (os.getpid()))

    def test_log_format_type_error(self):
        self.logger.init("test", use_syslog=False)

        self.logger.log(None, "log.class", 3, "%s", None)
        self.assertEqual(self.stderr_str.getvalue(),
                         "test[%d]: log.class(3): (nosession): %s\n" % (os.getpid(), '%s'))

    def test_log_format_value_error(self):
        self.logger.init("test", use_syslog=False)

        self.logger.log(None, "log.class", 3, "%s", ("format", "error"))
        self.assertEqual(self.stderr_str.getvalue(),
                         ("test[%d]: core.error(3): (nosession): Unable to format log message; error='not all arguments converted during string formatting'\n" +
                          "test[%d]: log.class(3): (nosession): %s\n") %
                         (os.getpid(), os.getpid(), '%s')
        )


    def test_uninitialized_state(self):
        with self.assertRaises(ValueError):
            self.logger.log("sessionid", "log.class", 3, "message")

        with self.assertRaises(ValueError):
            self.logger.use_syslog = False

if __name__ == '__main__':
    unittest.main()
