# -*- coding: utf-8 -*-

import unittest
import os
import shutil
from pybagit.bagit import BagIt


class CreateTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        if os.path.exists(os.path.join(os.getcwd(), 'test', 'newtestbag')):
            shutil.rmtree(os.path.join(os.getcwd(), 'test', 'newtestbag'))

    def test_minimal_bag_creation(self):
        newbag = BagIt(os.path.join(os.getcwd(), 'test', 'newtestbag'), extended=False)
        self.assertTrue(os.path.exists(os.path.join(os.getcwd(), 'test', 'newtestbag')))
        self.assertTrue(os.path.exists(os.path.join(os.getcwd(), 'test', 'newtestbag', 'bagit.txt')))
        self.assertTrue(os.path.exists(os.path.join(os.getcwd(), 'test', 'newtestbag', 'manifest-sha1.txt')))
        self.assertTrue(os.path.exists(os.path.join(os.getcwd(), 'test', 'newtestbag', 'data')))
        self.assertFalse(os.path.exists(os.path.join(os.getcwd(), 'test', 'newtestbag', 'bag-info.txt')))
        self.assertFalse(os.path.exists(os.path.join(os.getcwd(), 'test', 'newtestbag', 'fetch.txt')))
        self.assertFalse(os.path.exists(os.path.join(os.getcwd(), 'test', 'newtestbag', 'tagmanifest-sha1.txt')))

    def test_extended_bag_creation(self):
        newbag = BagIt(os.path.join(os.getcwd(), 'test', 'newtestbag'))
        self.assertTrue(os.path.exists(os.path.join(os.getcwd(), 'test', 'newtestbag')))
        self.assertTrue(os.path.exists(os.path.join(os.getcwd(), 'test', 'newtestbag', 'bagit.txt')))
        self.assertTrue(os.path.exists(os.path.join(os.getcwd(), 'test', 'newtestbag', 'manifest-sha1.txt')))
        self.assertTrue(os.path.exists(os.path.join(os.getcwd(), 'test', 'newtestbag', 'data')))
        self.assertTrue(os.path.exists(os.path.join(os.getcwd(), 'test', 'newtestbag', 'bag-info.txt')))
        self.assertTrue(os.path.exists(os.path.join(os.getcwd(), 'test', 'newtestbag', 'fetch.txt')))
        self.assertTrue(os.path.exists(os.path.join(os.getcwd(), 'test', 'newtestbag', 'tagmanifest-sha1.txt')))

    def test_unicode_characters_in_bagnam(self):
        newbag = BagIt(os.path.join(os.getcwd(), 'test', 'tëst'))
        self.assertTrue(os.path.exists(os.path.join(os.getcwd(), 'test', 'tëst')))

def suite():
    test_suite = unittest.makeSuite(CreateTest, 'test')
    return test_suite
