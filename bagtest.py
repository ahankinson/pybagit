import unittest
from test import bagmanifest
from test import bagfetch  # comment this out if no network connection
from test import bagcompress
from test import bagupdate
from test import bagcreate
from test import bagversion


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(bagmanifest.suite())
    test_suite.addTest(bagfetch.suite())  # comment this out if no network connection
    test_suite.addTest(bagcompress.suite())
    test_suite.addTest(bagupdate.suite())
    test_suite.addTest(bagcreate.suite())
    test_suite.addTest(bagversion.suite())
    return test_suite


runner = unittest.TextTestRunner()
runner.run(suite())
