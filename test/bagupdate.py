import unittest
import os
from pybagit.bagit import BagIt

class UpdateTest(unittest.TestCase):
    
    def setUp(self):
        self.bag = BagIt(os.path.join(os.getcwd(), 'test', 'testbag'))
    
    def tearDown(self):
        pass
    
    def test_update(self):
        self.bag.update()
        self.assertEquals(len(self.bag.bag_errors), 0)

def suite():
    test_suite = unittest.makeSuite(UpdateTest, 'test')
    return test_suite