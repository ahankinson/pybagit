# The MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell    import pybagit.bagit
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# sample code for how to create and update a bag.
import sys, os
import pybagit.bagit
from optparse import OptionParser

def create_new_bag(bagname):
    """ Takes a path to a bag. Returns a BagIt object. """
    bag = pybagit.bagit.BagIt(bagname)
    return bag
    
def make_test_files(bagobject):
    print("Creating Test Files...")
    # create some test directories
    os.makedirs(os.path.join(bagobject.data_directory, 'subdir', 'subsubdir1'))
    os.makedirs(os.path.join(bagobject.data_directory, 'subdir', 'subsubdir2'))
    os.makedirs(os.path.join(bagobject.data_directory, 'subdir', 'subsubdir3'))
    os.makedirs(os.path.join(bagobject.data_directory, 'subdir', 'subsubdir4'))
    
    # set up some random file contents
    t1 = "afdklsjanas.sm,nf.as,dfsdflsjkdhfalskjdfhasdfa"
    t2 = "zxm,v.cnzxclkjfsdiouaafdskjhasdfhalskdjfhasldkfja"
    t3 = "a0s98dfyasdfhaslkj938asiudhflaksjhdp9q8yiaudflaksd"
    t4 = "zx/v.,mzxc';lsdf;laksdjhfapda098dp9a78erewqkl;asdfj"
    
    testfiles = [t1, t2, t3, t4]
    
    i = 1
    for contents in testfiles:
        f = open(os.path.join(bagobject.data_directory, 'subdir', 'subsubdir{0}'.format(i), 'testfile.txt'), 'w')
        f.write(contents)
        f.close()
        i += 1
    
    print("Done!")
    

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-p', '--path', help="Path to save the new bag")
    parser.add_option('-b', '--bag', help='Bag Name')
    parser.add_option('-c', '--compress', help='Whether to compress the bag', action='store_true')
    (options, args) = parser.parse_args()
    
    if not options.path and options.bag:
        print "You need to specify a path and a bag name."
        sys.exit(0)
    
    # instantiate the bag.
    mybag = create_new_bag(os.path.join(options.path, options.bag))

    # set up some test files.
    make_test_files(mybag)
    
    # update the bag
    mybag.update()
    
    # validate the bag
    mybag.validate()
    
    # print some information about the bag.
    mybag.show_bag_info()
    
    # compress the bag (tgz is the default)
    if options.compress:
        print("Compressing.")
        pack = mybag.package(options.path)
        print("Package created at {0}".format(pack))

    print("Done!")
    # and we're done!
    
    
    

