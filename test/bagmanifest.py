import unittest
import os
from pybagit.bagit import BagIt


class ManifestTest(unittest.TestCase):
    def setUp(self):
        self.bag = BagIt(os.path.join(os.getcwd(), 'test', 'testbag'))

    def set_hash_md5(self):
        self.bag.set_hash_encoding('md5')
        self.assertEquals(self.hash_encoding, u'md5')

    def set_hash_sha1(self):
        self.bag.set_hash_encoding('sha1')
        self.assertEquals(self.hash_encoding, u'sha1')

    def test_sha1(self):
        self.bag.set_hash_encoding('sha1')
        self.bag.update()
        self.assertEquals(self.bag.manifest_contents[os.path.join('data', 'subdir', 'subsubdir', 'angry.jpg')],
                u'c5913ae67aa40398f1182e52d2fa2c2e4c08f696')

    def test_md5(self):
        self.bag.set_hash_encoding('md5')
        self.bag.update()
        self.assertEquals(self.bag.manifest_contents[os.path.join('data', 'subdir', 'subsubdir', 'angry.jpg')],
                '5f294603675cb6c0f83cef9316bb5be7')

    def test_sha1_manifest(self):
        self.bag.set_hash_encoding('sha1')
        self.bag.update()
        self.assertEquals(os.path.basename(self.bag.manifest_file),
                'manifest-sha1.txt')

    def test_md5_manifest(self):
        self.bag.set_hash_encoding('md5')
        self.bag.update()
        self.assertEquals(os.path.basename(self.bag.manifest_file),
                'manifest-md5.txt')


def suite():
    test_suite = unittest.makeSuite(ManifestTest, 'test')
    return test_suite
