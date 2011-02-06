#!/usr/bin/env python

import multiprocessing
from optparse import OptionParser
import os, sys
import hashlib
import codecs
import time
from pybagit.exceptions import *

# declare a default hashalgorithm
HASHALG = 'sha1'
ENCODING = "utf-8"

def write_manifest(datadir, encoding):
    bag_root = os.path.split(os.path.abspath(datadir))[0]
    
    manifest_file = "manifest-{0}.txt".format(HASHALG)
    
    p = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    mapresult = p.map_async(csumfile, dirwalk(datadir)).get()
    p.close()
    p.join()
    
    mfile = codecs.open(os.path.join(bag_root, manifest_file), 'w', encoding)
    for csum,cfile in mapresult:
        mfile.write("{0} {1}\n".format(csum, os.path.relpath(cfile, bag_root)))
    mfile.close()
    
def dirwalk(datadir):
    datafiles = []
    for dirpath, dirnames, filenames in os.walk(datadir):
        for fn in filenames:
            datafiles.append(os.path.join(dirpath, fn))
    return datafiles

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
    
    if len(args) < 1:
        parser.error("You must specify a data directory")
    write_manifest(args[0], ENCODING)
    