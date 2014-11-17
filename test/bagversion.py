import unittest
import os
from pybagit.bagit import BagIt


class VersionTest(unittest.TestCase):
    def setUp(self):
        self.bag = BagIt(os.path.join(os.getcwd(), 'test', 'testbag'))

    def tearDown(self):
        pass

    def test_versions(self):
        self.assertEquals(self.bag.bag_major_version, 0)
        self.assertEquals(self.bag.bag_minor_version, 96)
        binfo = self.bag.get_bag_info()
        self.assertEquals(binfo['version'], '0.96')
        self.assertEquals(binfo['encoding'], 'utf-8')
        self.assertEquals(binfo['hash'], 'sha1')


def suite():
    test_suite = unittest.makeSuite(VersionTest, 'test')
    return test_suite
