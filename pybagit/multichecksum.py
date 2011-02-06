#!/usr/bin/env python

import multiprocessing
from optparse import OptionParser
import os, sys
import hashlib
import codecs

from pybagit.exceptions import *

# declare a default hashalgorithm
HASHALG = 'md5'
ENCODING = "utf-8"

def write_manifest(manfile, datadir, encoding):
    bag_root = os.path.split(os.path.abspath(manfile))[0]
    p = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    mfile = codecs.open(manfile, 'w', encoding)
    for csum, cfile in p.map(csumfile, dirwalk(datadir)):
        mfile.write("{0} {1}\n".format(csum, os.path.relpath(cfile, bag_root)))
    p.close()
    p.join()
    mfile.close()
    
def dirwalk(datadir):
    for dirpath, dirnames, filenames in os.walk(datadir):
        for fn in filenames:
            yield os.path.join(dirpath, fn)

def csumfile(filename):
    """ Based on 
        http://abstracthack.wordpress.com/2007/10/19/calculating-md5-checksum/
    """
    hashalg = getattr(hashlib, HASHALG)() # == 'hashlib.md5' or 'hashlib.sha1'
    blocksize = 0x10000
    
    def __upd(m, data):
        m.update(data)
        return m
        
    fd = open(filename, 'rb')
    
    try:
        contents = iter(lambda: fd.read(blocksize), "")
        m = reduce(__upd, contents, hashalg)
    finally:
        fd.close()
    
    return (m.hexdigest(), filename)


if __name__ == "__main__":
    parser = OptionParser()
    usage = "%prog [options] arg1 arg2"
    parser.add_option("-a", "--algorithm", action="store", help="checksum algorithm to use (sha1|md5)")
    parser.add_option("-c", "--encoding", action="store", help="File encoding to write manifest")
    (options,args) = parser.parse_args()
    
    if options.algorithm:
        if not options.algorithm in ('md5', 'sha1'):
            raise BagCheckSumNotValid('You must specify either "md5" or "sha1" as the checksum algorithm')
        HASHALG = options.algorithm
    
    if options.encoding:
        ENCODING = options.encoding
    
    if len(args) < 2:
        parser.error("You must specify both a manifest file and a data directory")
    
    write_manifest(args[0], args[1], ENCODING)
    sys.exit(0)
    