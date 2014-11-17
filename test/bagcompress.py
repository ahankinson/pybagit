import unittest
import os
import shutil
from pybagit.bagit import BagIt


class CompressTest(unittest.TestCase):

    def setUp(self):
        self.bag = BagIt(os.path.join(os.getcwd(), 'test', 'testbag'))

    def tearDown(self):
        if os.path.exists(os.path.join(os.getcwd(), 'test', 'testbag.tgz')):
            os.remove(os.path.join(os.getcwd(), 'test', 'testbag.tgz'))
        if os.path.exists(os.path.join(os.getcwd(), 'test', 'testbag.zip')):
            os.remove(os.path.join(os.getcwd(), 'test', 'testbag.zip'))
        if os.path.exists(os.path.join(os.getcwd(), 'test', 'newzipbag')):
            shutil.rmtree(os.path.join(os.getcwd(), 'test', 'newzipbag'))
        if os.path.exists(os.path.join(os.getcwd(), 'test', 'newtgzbag')):
            shutil.rmtree(os.path.join(os.getcwd(), 'test', 'newtgzbag'))
        if os.path.exists(os.path.join(os.getcwd(), 'test', 'newzipbag.zip')):
            os.remove(os.path.join(os.getcwd(), 'test', 'newzipbag.zip'))
        if os.path.exists(os.path.join(os.getcwd(), 'test', 'newtgzbag.tgz')):
            os.remove(os.path.join(os.getcwd(), 'test', 'newtgzbag.tgz'))

    def test_compress_tgz(self):
        self.bag.package(os.path.join(os.getcwd(), 'test'))
        self.assertTrue(os.path.exists(os.path.join(os.getcwd(), 'test', 'testbag.tgz')))

    def test_compress_zip(self):
        self.bag.package(os.path.join(os.getcwd(), 'test'), method='zip')
        self.assertTrue(os.path.exists(os.path.join(os.getcwd(), 'test', 'testbag.zip')))

    def test_uncompress_tgz(self):
        # create an empty tgz bag.
        newbag = BagIt(os.path.join(os.getcwd(), 'test', 'newtgzbag'))
        newbag.package(os.path.join(os.getcwd(), 'test'))
        # remove the created bag directory
        shutil.rmtree(os.path.join(os.getcwd(), 'test', 'newtgzbag'))
        # this should leave us with just newtgzbag.tgz
        tgzbag = BagIt(os.path.join(os.getcwd(), 'test', 'newtgzbag.tgz'))
        self.assertTrue(os.path.exists(tgzbag.bag_directory))

    def test_uncompress_zip(self):
        # create an empty zip bag.
        newbag = BagIt(os.path.join(os.getcwd(), 'test', 'newzipbag'))
        newbag.package(os.path.join(os.getcwd(), 'test'), method='zip')
        # remove the created bag directory
        shutil.rmtree(os.path.join(os.getcwd(), 'test', 'newzipbag'))
        # this should leave us with just newtgzbag.tgz
        zipbag = BagIt(os.path.join(os.getcwd(), 'test', 'newzipbag.zip'))
        self.assertTrue(os.path.exists(zipbag.bag_directory))


def suite():
    test_suite = unittest.makeSuite(CompressTest, 'test')
    return test_suite
