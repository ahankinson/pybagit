import unittest
import os
from pybagit.bagit import BagIt


class FetchTest(unittest.TestCase):
    ### THESE MAY FAIL if the Websites change their files. In that case,
    ### just comment this test out, or replace the assertion with a new
    ### SHA1 Checksum.
    def setUp(self):
        self.bag = BagIt(os.path.join(os.getcwd(), 'test', 'testbag'))
        self.test_fetch_contents = [{'filename': u'data/bagitspec.pdf',
          'length': u'-',
          'url': u'http://www.digitalpreservation.gov/documents/bagitspec.pdf'}]

    def tearDown(self):
        # if os.path.exists(os.path.join(os.getcwd(), 'test', 'testbag', 'data', 'bagitspec.pdf')):
        #     os.remove(os.path.join(os.getcwd(), 'test', 'testbag', 'data', 'bagitspec.pdf'))
        if os.path.exists(os.path.join(os.getcwd(), 'test', 'testbag', 'data', 'stealin_mah_bag.jpg')):
            os.remove(os.path.join(os.getcwd(), 'test', 'testbag', 'data', 'stealin_mah_bag.jpg'))
        if os.path.exists(os.path.join(os.getcwd(), 'test', 'testbag', 'data', 'bagitspec.pdf')):
            os.remove(os.path.join(os.getcwd(), 'test', 'testbag', 'data', 'bagitspec.pdf'))
        self.bag.add_fetch_entries(self.test_fetch_contents, append=False)

    def test_fetch_contents(self):
        self.assertEquals(self.bag.fetch_contents, self.test_fetch_contents)

    def test_can_fetch(self):
        self.bag.fetch()
        self.assertTrue(os.path.exists(os.path.join(os.getcwd(), 'test', 'testbag', 'data', 'bagitspec.pdf')))

    def test_can_fetch_and_validate(self):
        self.bag.fetch(validate_downloads=True)
        self.assertEquals(self.bag.manifest_contents['data/bagitspec.pdf'],
            '4649c6540ac4e4dcf271ca236abfe62faa4d7f08')

    def set_fetch_contents(self):
        self.bag.add_fetch_entries([{'url': 'http://icanhascheezburger.files.wordpress.com/2007/06/stealing_my_bag.jpg',
                'filename': os.path.join('data','stealin_mah_bag.jpg')}])
        self.assertTrue(os.path.exists(os.path.join(os.getcwd(), 'test', 'testbag', 'data', 'stealin_mah_bag.jpg')))


def suite():
    test_suite = unittest.makeSuite(FetchTest, 'test')
    return test_suite
