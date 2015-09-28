""" Read and create BagIt files. """

__author__ = "Andrew Hankinson (andrew.hankinson@mail.mcgill.ca)"
__version__ = "1.5"
__date__ = "2011"
__copyright__ = "Creative Commons Attribution"
__license__ = """The MIT License

                Permission is hereby granted, free of charge, to any person obtaining a copy
                of this software and associated documentation files (the "Software"), to deal
                in the Software without restriction, including without limitation the rights
                to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
                copies of the Software, and to permit persons to whom the Software is
                furnished to do so, subject to the following conditions:

                The above copyright notice and this permission notice shall be included in
                all copies or substantial portions of the Software.

                THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
                IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
                FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
                AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
                LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
                OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
                THE SOFTWARE."""

import subprocess
import tempfile
import hashlib
import zipfile
import tarfile
import sys
import os
import shutil
import codecs
import string
import random
import urllib
import re

import time

# import bagit-specific exceptions.
from pybagit.exceptions import *


class BagIt:
    def __init__(self, bag, validate=False, extended=True, fetch=False):
        """ Creates a Bag object. If file doesn't exist, it initializes an
            empty directory with empty files; if it does, it reads in the
            existing files.

            If validate is True, it runs the validate() method to check the bag's
            consistency and completeness.

            If fetch is True, it fetches the files from fetch.txt and places
            them in the appropriate directory.
        """

        self._bag              = bag  # bag as passed in. Could be either directory or file name, and may not exist.
        self.extended          = extended  # True if it is an 'extended' bag; False if it is not.
        self.hash_encoding     = u'sha1'  # default hash encoding. Could also be md5. Should always be lowercase.
        self.bag_major_version = 0
        self.bag_minor_version = 96   # default bagit version. Set to the latest approved version.
        self.tag_file_encoding = u'utf-8'  # default text encoding. always lower case.
        self.data_directory    = None  # path to the bag data directory
        self.bag_directory     = None  # path to the bag directory
        self.bagit_file        = None  # path to the bagit.txt file
        self.manifest_file     = None  # path to the manifest.*.txt file
        self.tag_manifest_file = None  # path to the tagmanifest.*.txt file
        self.fetch_file        = None
        self.baginfo_file      = None
        self.manifest_contents = None  # dictionary containing the current manifest contents.
        self.tag_manifest_contents = None
        self.fetch_contents    = None
        self.baginfo_contents  = None
        self.bag_compression   = None  # compression type (if any)
        self.bag_errors        = []  # list of bag validation errors
        self.platform          = sys.platform  # set the platform value.

        module_path = os.path.dirname(os.path.abspath(__file__))
        self._path_to_multichecksum = os.path.join(module_path, "multichecksum.py")

        try:
            if os.path.exists(self._bag):
                self._open_bag()
                return
            else:
                raise BagDoesNotExistError("Bag does not exist at {0}".format(self._bag))
        except BagDoesNotExistError:
            self._create_bag()
        finally:
            if validate:
                self.validate()

    def is_valid(self):
        """ Returns True if no validation errors have been reported."""
        if len(self.bag_errors) == 0:
            return True
        else:
            return False

    def is_extended(self):
        """ Checks to see if the bag contains optional
            tag manifest, fetch or metadata files.
        """
        return self.extended

    def get_bag_info(self):
        """ Returns a dictionary containing the version, encoding and selected
            hash encoding.
        """
        info = {}
        info['version'] = "{0}.{1}".format(self.bag_major_version, self.bag_minor_version)
        info['encoding'] = self.tag_file_encoding
        info['hash'] = self.hash_encoding
        return info

    def get_data_directory(self):
        """ Returns the path to the data directory. """
        return self.data_directory

    def get_tag_files(self):
        # !!! TODO
        pass

    def get_hash_encoding(self):
        """ Returns the hash encoding of the bag. Either 'sha1' or 'md5'. """
        return self.hash_encoding

    def set_hash_encoding(self, algorithm):
        """ Sets the bag checksum algorithm. """
        if algorithm.lower() not in ('md5', 'sha1'):
            raise BagCheckSumNotValid('You must specify either "md5" or "sha1".')
        self.hash_encoding = unicode(algorithm)
        self.manifest_file = os.path.join(self.bag_directory, "manifest-{0}.txt".format(self.hash_encoding))

    def show_bag_info(self):
        """ Shows some information on the bag, it's contents and metadta.

            !!! TODO: Make this look prettier.
        """
        print("Bag Version: {0}.{1}".format(self.bag_major_version, self.bag_minor_version))
        print("Tag File Encoding: {0}".format(self.tag_file_encoding))
        bagtype = "Base" if not self.extended else "Extended"
        print("Bag Type: {0}".format(bagtype))
        print("\n")
        print((" " * 20) + "Manifest Contents")
        print("CHECKSUMS" + (" " * 33) + "FILENAMES")
        print("-" * 100)
        for k, v in self.manifest_contents.iteritems():
            print("{0}  {1}".format(v, k))

        if self.extended:
            print("\n")
            print((" " * 20) + "Tag Manifest Contents")
            print("CHECKSUMS" + (" " * 33) + "FILENAMES")
            print("-" * 100)
            for k, v in self.tag_manifest_contents.iteritems():
                print("{0}  {1}".format(v, k))

        print("\n")
        print("Bag Errors")
        if self.bag_errors:
            print("ERROR CODE" + (" " * 10) + "MESSAGE")
            print("-" * 50)
            for error in self.bag_errors:
                print("{0} {1}".format(error[0], error[1]))
        else:
            print("-" * 50)
            print("No Errors.")

        print("\n\n")

    def get_bag_contents(self):
        """ Returns a list containing all files in the data directory. """
        data = os.walk(self.data_directory)
        baglist = []
        for dir in data:
            for file in dir[2]:
                baglist.append("{0}/{1}".format(dir[0], file))
        return baglist

    def get_bag_errors(self, validate=False):
        """ Returns the bag errors. If validate is True, it will re-run the
            bag validation.
        """
        if validate:
            self.validate()
        return self.bag_errors

    def validate(self):
        """ Runs a suite of checks to determine the validity of a bag.
            Returns any errors it found.
        """
        errors = []

        # verify the presence of the bagit.txt file
        try:
            codecs.open(self.bagit_file, 'r', self.tag_file_encoding)
        except Exception, e:
            errors.append(('bagit.txt', 'bagit.txt file does not exist: {0}'.format(e)))

        # verify the presence of the data directory
        try:
            if not os.path.exists(self.data_directory):
                raise BagIsNotValidError('Not Found')
        except (BagIsNotValidError, Exception), e:
            errors.append(('data', 'data directory could not be found: e'.format(e)))

        # verify the presence of the manifest-(sha1|md5).txt file
        try:
            codecs.open(self.manifest_file, 'r', self.tag_file_encoding)
        except Exception, e:
            errors.append(('manifest-{0}.txt'.format(self.hash_encoding), 'manifest-{0}.txt file does not exist: {1}'.format(self.hash_encoding, e)))

        try:
            # verify the contents of the manifest-(sha1|md5).txt file.
            if not os.path.exists(self.data_directory):
                raise BagIsNotValidError('Data Directory Not Found')
            elif not os.path.exists(self.manifest_file):
                raise BagIsNotValidError('Manifest File Not Found')
            else:
                for dir in os.walk(self.data_directory):
                    for file in dir[2]:
                        csum = self._calculate_checksum(os.path.join(dir[0], file))
                        relpath = os.path.relpath(os.path.join(dir[0], file), self.bag_directory)
                        if relpath in self.manifest_contents:
                            if cmp(self.manifest_contents[relpath], csum) != 0:
                                errors.append((relpath, 'Incorrect filename or checksum in manifest'))
                        else:
                            errors.append((relpath, 'File is not correct in manifest'))
        except (BagIsNotValidError, Exception), e:
            errors.append(('checksum verification', 'Problems verifying the manifest: {0}'.format(e)))

        self.bag_errors = errors
        return self.bag_errors

    def update(self):
        """ Scans the data directory, adds any new files it finds to the
            manifest, and removes any files from the manifest that it does not
            find in the directory.
        """

        # clean up any old manifest files. We'll be regenerating them later.
        filelist = os.listdir(self.bag_directory)
        tagmanifests = [f for f in filelist
                        if re.match(r"^tagmanifest-(sha1|md5)\.txt", f)]
        datamanifests = [f for f in filelist
                         if re.match(r"^manifest-(sha1|md5)\.txt", f)]
        old_manifests = tagmanifests + datamanifests
        for man in old_manifests:
            os.unlink(os.path.join(self.bag_directory, man))

        # add an empty .keep file in empty directories.
        for dirpath, dirname, fnames in os.walk(self.data_directory):
            if not os.listdir(dirpath):
                open(os.path.join(dirpath, '.keep'), 'w').close()

        # Sanitize Data Directory
        for dirpath, dirname, fnames in os.walk(self.data_directory):
            for fname in fnames:
                newfile = self._sanitize_filename(fname)
                if newfile != fname:
                    os.rename(os.path.join(dirpath, fname), os.path.join(dirpath, newfile))

        # checksum the data directory
        cmd = [sys.executable, self._path_to_multichecksum, "-a", self.hash_encoding, "-c", self.tag_file_encoding, self.data_directory]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

        while p.returncode is None:
            time.sleep(0.1)
            p.poll()

        # read in the manifest to an instance variable
        self._read_manifest_to_dict()

        # clean out any previous tag manifest contents.
        self.tag_manifest_contents = {}
        for f in ['bagit.txt', 'bag-info.txt', 'fetch.txt', self.manifest_file]:
            csum = self._calculate_checksum(os.path.join(self.bag_directory, f))
            relp = os.path.relpath(os.path.join(self.bag_directory, f), self.bag_directory)
            self.tag_manifest_contents[relp] = csum

        # write out the tag manifest
        self._write_dict_to_manifest(mode="t")

        # read it back in
        self._read_manifest_to_dict(mode="t")

    def fetch(self, validate_downloads=False):
        """ Downloads files into the data directory.

        """

        for entry in self.fetch_contents:
            try:
                if not os.path.exists(os.path.join(self.bag_directory, entry['filename'])):
                    dwnlddir = os.path.join(self.bag_directory, os.path.dirname(entry['filename']))
                    filename = os.path.basename(entry['filename'])
                    if not os.path.exists(dwnlddir):
                        os.makedirs(dwnlddir)
                    urllib.urlretrieve(entry['url'], os.path.join(dwnlddir, filename))
                else:
                    # file already downloaded to bag. Continue.
                    continue
            except Exception, e:
                self.bag_errors.append(('fetch', 'URL {0} could not be downloaded {1}'.format(entry['url'], e)))
                continue

        if validate_downloads:
            self.update()
            self.validate()

    def add_fetch_entries(self, fetch_entry, append=True):
        """ Takes a list containing a dictionary of URLs and filenames.

            e.g. [{'url':'http://www.example.com/path/to/file.txt',
                    'filename':'data/path/to/file.txt'}]

            !!! TODO calculate actual length of file, instead of encoding '-'
        """
        fetch_items = []
        for item in fetch_entry:
            fetch_items.append({'url': item['url'],
                                'length': '-',
                                'filename': item['filename'],
                                })

        # !!! TODO: implement live updating of the fetch list/dictionary
        if append:
            self.fetch_contents.extend(fetch_items)
        else:
            self.fetch_contents = fetch_items

        self._write_list_to_fetch()

    def package(self, destination, method="tgz"):
        """ zip the bag into a package. Can be either .zip or .tar.gz.

            You must specify a destination to copy the final package to.
         """
        if method.lower() not in ('zip', 'tgz'):
            raise BagError('You must specify either "zip" or "tgz"')

        package = self._compress_bag(method)
        shutil.move(package, destination)
        if os.path.exists(os.path.join(destination, os.path.basename(package))):
            return os.path.join(destination, os.path.basename(package))
        else:
            raise BagError("Uh oh! We've lost track of a file...")

    # private
    def _create_bag(self):
        """ Initializes a new bag directory. """

        current_path = os.getcwd()
        try:
            if os.path.isabs(self._bag):
                os.mkdir(self._bag)
            else:
                os.mkdir(os.path.join(current_path, self._bag))
        except OSError, e:
            raise BagCouldNotBeCreatedError("Bag Could Not Be Created: {0}".format(e))
            return
        except Exception, e:
            raise BagError('Could not create directory {0}').format(os.path.join(current_path, self._bag))
            return

        self.bag_directory = os.path.join(current_path, self._bag)
        self.data_directory = os.path.join(self.bag_directory, 'data')
        os.mkdir(self.data_directory)

        version_id = u"BagIt-Version: {0}.{1}\n".format(self.bag_major_version,
                                                     self.bag_minor_version)
        encoding = u"Tag-File-Character-Encoding: {0}\n".format(self.tag_file_encoding.upper())

        self.bagit_file = os.path.join(self.bag_directory, 'bagit.txt')
        self.manifest_file = os.path.join(self.bag_directory, 'manifest-{0}.txt'.format(self.hash_encoding))

        bfile_contents = (version_id, encoding)
        bfile = codecs.open(self.bagit_file, 'w', self.tag_file_encoding)
        bfile.writelines(bfile_contents)
        bfile.close()

        # just create the manifest file. we'll add stuff later.
        tfile = codecs.open(self.manifest_file, 'w', self.tag_file_encoding)
        tfile.close()

        self._read_manifest_to_dict()  # this should be empty, but we'll do it to ensure consistency.

        if self.extended:
            self.tag_manifest_file = os.path.join(self.bag_directory, 'tagmanifest-{0}.txt'.format(self.hash_encoding))
            tmfile = codecs.open(self.tag_manifest_file, 'w', self.tag_file_encoding)
            tmfile.close()
            self._read_manifest_to_dict(mode="t")

            self.fetch_file = os.path.join(self.bag_directory, 'fetch.txt')
            fetchfile = codecs.open(self.fetch_file, 'w', self.tag_file_encoding)
            fetchfile.close()
            self._read_fetch_to_list()

            self.baginfo_file = os.path.join(self.bag_directory, 'bag-info.txt')
            binfofile = codecs.open(self.baginfo_file, 'w', self.tag_file_encoding)
            binfofile.close()
            self._read_baginfo_to_dict()

    def _calculate_checksum(self, filepath):
        """ Taken from
            http://abstracthack.wordpress.com/2007/10/19/calculating-md5-checksum/
        """

        # getattr converts the hash_encoding to a method argument for hashlib.
        block_size = 0x10000
        hashalg = getattr(hashlib, self.hash_encoding)()  # == 'hashlib.md5' or 'hashlib.sha1'

        def upd(m, data):
            m.update(data)
            return m
        fd = open(filepath, 'rb')

        try:
            contents = iter(lambda: fd.read(block_size), "")
            m = reduce(upd, contents, hashalg)
        finally:
            fd.close()
        return m.hexdigest()

    def _open_bag(self):
        """ This does its best to open a bag, even if the bag is malformed.

            Any problems should be caught with the 'validate bag' function later on,
            so that we can deal with them gracefully.
        """

        if self._is_compressed() is True:
            # TODO: combine this with the more robust regex from the sanitize filenames method...
            names = re.match(r"^(?P<basename>.*)\.(?P<ext>(zip|tar\.gz|tgz))", self._bag)
            base = names.group('basename')
            bdir = self._uncompress_bag(base)
            self.bag_directory = bdir
        else:
            self.bag_directory = os.path.abspath(self._bag)

        try:
            self.bagit_file = os.path.join(self.bag_directory, 'bagit.txt')
            bfile = codecs.open(self.bagit_file, 'r', self.tag_file_encoding)
            bfile_contents = bfile.read()
            bfile.close()

            self.bag_major_version, self.bag_minor_version = self._parse_version_string(bfile_contents)
            self.tag_file_encoding = self._parse_encoding_string(bfile_contents).lower()  # tag file encoding is always lower case.
        except:
            self.bag_errors.append(('bagit', 'Had problems reading the Bagit.txt file.'))

        filelist = os.listdir(self.bag_directory)

        if len(filelist) > 0:
            manifest = filter(lambda f: re.match(r"^manifest-(sha1|md5)\.txt", f), filelist)  # search for the right manifest file.
            if manifest:
                try:
                    self.hash_encoding = unicode(re.search(r"(?P<encoding>(sha1|md5))", manifest[0]).group('encoding'))
                    self.manifest_file = os.path.join(self.bag_directory, manifest[0])
                    self._read_manifest_to_dict()
                except:
                    self.bag_errors.append(('manifest', 'Had problems reading the manifest file.'))

            self.data_directory = os.path.join(self.bag_directory, 'data')

            tmanifest = filter(lambda f: re.match(r"^tagmanifest-(sha1|md5)\.txt", f), filelist)  # search for the right manifest file.
            if tmanifest:
                try:
                    self.tag_manifest_file = os.path.join(self.bag_directory, tmanifest[0])
                    self._read_manifest_to_dict(mode='t')
                except:
                    self.bag_errors.append(('tagmanifest', 'Had problems reading the tagmanifest file.'))

            if os.path.exists(os.path.join(self.bag_directory, 'fetch.txt')):
                try:
                    self.fetch_file = os.path.join(self.bag_directory, 'fetch.txt')
                    self._read_fetch_to_list()
                except:
                    self.bag_errors.append(('fetch', 'Had problems reading fetching the files.'))

            if os.path.exists(os.path.join(self.bag_directory, 'bag-info.txt')):
                try:
                    self.baginfo_file = os.path.join(self.bag_directory, 'bag-info.txt')
                    self._read_baginfo_to_dict()
                except:
                    self.bag_errors.append(('baginfo', 'Had problems reading the bag info file.'))

    def _is_compressed(self):
        """ returns true if the bag is compressed; false if not."""
        if os.path.isdir(self._bag):
            return False
        elif zipfile.is_zipfile(self._bag) is True:
            self.bag_compression = 'zip'
            return True
        elif tarfile.is_tarfile(self._bag):
            self.bag_compression = 'tgz'
            return True
        else:
            raise BagFormatNotRecognized("Could not determine bag format.")
            return False

    def _uncompress_bag(self, bagbase):
        """ unzips a bag. """
        tdir = os.path.join(tempfile.mkdtemp(prefix='bagit_'), bagbase)
        if self.bag_compression is None:
            return  # we should never have this, but just in case.
        elif self.bag_compression is 'zip':
            zfil = zipfile.ZipFile(self._bag)
            zfil.extractall(tdir)
            zfil.close()
        elif self.bag_compression is 'tgz':
            tfil = tarfile.open(self._bag)
            tfil.extractall(path=tdir)
            tfil.close()
        else:
            raise BagFormatNotRecognized('Could not unzip bag.')

        return tdir

    def _compress_bag(self, method="tgz", zip64=True):
        """ Compresses a bag using a specified method.

            Compresses in a temp directory. Returns a path to that file.
        """

        tdir = tempfile.mkdtemp(prefix='bagit_')
        bagname = ".".join((os.path.basename(self.bag_directory), method))
        compressed_file = os.path.join(tdir, bagname)

        if method is "zip":
            z = zipfile.ZipFile(compressed_file, mode='w',
                                compression=zipfile.ZIP_DEFLATED,
                                allowZip64=zip64)
            for d in os.walk(self.bag_directory):
                for f in d[2]:
                    # zipfile write takes two arguments. The first is the
                    # *absolute* path of the file to compress, and the second
                    # is the *relative* path to the root of the zipfile.
                    z.write(os.path.join(d[0], f),
                            os.path.relpath(os.path.join(d[0], f),
                                            self.bag_directory))
            z.close()
        else:
            t = tarfile.open(name=compressed_file, mode='w:gz')
            # why couldn't zipfile be like this?? So nice...
            t.add(self.bag_directory,
                  arcname=os.path.relpath(self.bag_directory,
                                          self.bag_directory), recursive=True)
            t.close()

        return compressed_file

    def _parse_encoding_string(self, string):
        re_vstring = re.compile(
            r"Tag-File-Character-Encoding: (?P<encoding>.*)", re.IGNORECASE)
        results = re.search(re_vstring, string)
        return results.group('encoding')

    def _parse_version_string(self, string):
        re_vstring = re.compile(
            r"BagIt-Version: (?P<major>\d+)\.(?P<minor>\d+)", re.IGNORECASE)
        results = re.search(re_vstring, string)
        return (int(results.group('major')), int(results.group('minor')))

    def _read_fetch_to_list(self):
        """ Format:
            URL LENGTH FILENAME = [{'url':'', 'length':'', filename:''},...]
        """
        ffile = codecs.open(self.fetch_file, 'r', self.tag_file_encoding)
        fcontents = ffile.readlines()
        ffile.close()
        fetch = []

        try:
            for it in fcontents:
                url, length, filename = it.split(" ")
                fname = os.path.normpath(filename.strip())
                line = {'url': url.strip(), 'length': length.strip(),
                        'filename': fname}
                fetch.append(line)
            self.fetch_contents = fetch
        except Exception:
            self.bag_errors.append(('fetch', 'Fetch file may be malformed.'))
            raise BagError('Fetch file may be malformed.')

    def _write_list_to_fetch(self):
        """ Writes the fetch list out to the fetch.txt file.

            !!! TODO: Calculate actual file length
        """
        ffile = codecs.open(self.fetch_file, 'w', self.tag_file_encoding)
        for item in self.fetch_contents:  # fetch_contents is a list, not a dictionary!
            line = "{url} {length} {filename}\n".format(url=item['url'],
                                                        length='-',
                                                        filename=self._ensure_unix_pathname(item['filename']))
            ffile.write(line)
        ffile.close()

    def _read_baginfo_to_dict(self):
        """ Format:
            {'Field-Name':'Value'}

            The baginfo files are similar to RFC-822. This code is inspired by
            http://code.activestate.com/recipes/576996/

        """
        bag_info = {}
        bifile = codecs.open(self.baginfo_file, 'r', self.tag_file_encoding)
        bicontents = bifile.readlines()
        bifile.close()

        try:
            for line in bicontents:
                if line[0] == ' ' or line[0] == "\t":
                    # we've got a continued line, signified by an indent.
                    bag_info[prev_key] = " ".join((bag_info[prev_key], line.lstrip().rstrip()))
                else:
                    # we've got a new entry
                    key, val = line.split(':', 1)
                    bag_info[key] = val.lstrip().rstrip()
                    prev_key = key
        except Exception, e:
            raise BagError('The bag-info.txt file may be malformed. Please re-check it.')
            self.bag_errors('bag-info', 'The bag-info.txt file may be malformed.')

        self.baginfo_contents = bag_info

    def _update_manifest_filenames(self):
        self.manifest_file = os.path.join(self.bag_directory, "manifest-{0}.txt".format(self.hash_encoding))
        self.tag_manifest_file = os.path.join(self.bag_directory, "tagmanifest-{0}.txt".format(self.hash_encoding))

    def _write_dict_to_manifest(self, mode="d"):
        # ensure we're working with the latest files.
        self._update_manifest_filenames()

        if mode == "d":
            mparse = self.manifest_file
            contents = self.manifest_contents
        elif mode == "t":
            mparse = self.tag_manifest_file
            contents = self.tag_manifest_contents

        mfile = codecs.open(mparse, 'w', self.tag_file_encoding)
        for k, v in contents.iteritems():
            # unix pathnames are the only ones acceptable in a manifest file.
            # this will ensure that if we're on Windows, we're still writing
            # unix/style/pathnames, even though the manifest contains windows\style\pathnames.
            if self.platform == "win32":
                k = self._ensure_unix_pathname(k)

            # we write this to the manifest reversing the checksum & path.
            mfile.write(u"{0} {1}\n".format(v, k))
        mfile.close()

    def _read_manifest_to_dict(self, mode="d"):
        """ We munge the manifest entries like this:
                - if we're in sha1, the keylen is 40
                - if we're in md5, the keylen is 32
            The manifest entries are split at the end of the key length
            and then assigned to the manifest dictionary, indexed by path name

            The mode parameter switches the manifest file that we are parsing.
                - "d" is for the data manifest file ('manifest.??.txt')
                - "t" is for the tag manifest file ('tagmanifest.??.txt')

            *PHEW!* """

        keylen = '40' if self.hash_encoding == u'sha1' else '32'

        # ensure we're always getting the latest file.
        self._update_manifest_filenames()

        if mode == "d":
            mparse = self.manifest_file
        elif mode == "t":
            mparse = self.tag_manifest_file

        mfile = codecs.open(mparse, 'r', self.tag_file_encoding)
        mcontents = mfile.readlines()
        mfile.close()
        manifest = {}
        # we have to use old-style string formatting here.
        splitreg = re.compile(r"^([a-f0-9]{%s})" % (keylen,))
        if len(mcontents) > 0:
            for line in mcontents:
                # we index by pathname, since that's almost certainly
                # unique (checksums can be the same for duplicate files...)
                # this is contrary to the way it's stored in the manifest,
                # so we simply reverse the input.
                ent = re.split(splitreg, line)
                # clean up the entries: discard empty items and strip whitespace
                # from the beginning of the file path.
                v, k = [x.lstrip().rstrip() for x in ent if len(x) != 0]

                # for Windows compatibility when *reading* a bag we need to ensure
                # that it can resolve the paths. This will set any forward slashes to back
                # slashes so that Windows can figure out where the file is.
                if self.platform == "win32":
                    k = os.path.normpath(k)

                manifest[k] = v

        if mode == "d":
            self.manifest_contents = manifest
        elif mode == "t":
            self.tag_manifest_contents = manifest

    def _sanitize_filename(self, filename):
        """ Replaces or removes characters from filenames to make them
            not evil.
        """
        # update the file_extensions regex if you encounter any special compound file extensions.
        # We'll preserve entries in this as the extension, instead of just splitting
        # at the last dot. Remember to keep the first dot intact!
        # it will match extension up to 5 characters long.
        file_extensions = re.compile(r"(\.tar\.gz$|\.tar\.bz2$|\.tar\.gzip$|\.tar\.bzip2$|\.[\w+]{5}$)")

        underscore = re.compile(r"([ ])")
        replace = re.compile(r"(CON|PRN|AUX|NUL|COM1|COM2|COM3|COM4|COM5|COM6|COM7|COM8|\
                                COM9|LPT1|LPT2|LPT3|LPT4|LPT5|LPT6|LPT7|LPT8|LPT9)")
        remove = re.compile(r"(\.{2}|[~\^@!#%&\*\/:'?\"<>\|])")

        split_fname = re.split(file_extensions, filename)
        split_fname = [x for x in split_fname if len(x) != 0]  # get rid of any empty entries.

        base_fname = split_fname[0]
        # deal with leading-dot hidden files.
        if len(split_fname) > 1:
            ext_fname = split_fname[1]
        else:
            ext_fname = ''

        # if we're replacing characters because of an invalid name, we'll lowercase
        # the name and add 4 random characters. We do this because simply stripping
        # them may cause filename collisions.
        und_filename = re.sub(underscore, "_", base_fname)
        rep_filename = re.sub(replace, "_".join((base_fname.lower(), "".join((random.sample(string.ascii_lowercase, 4))))), und_filename)
        rem_filename = re.sub(remove, "", rep_filename)
        clean_filename = "".join((rem_filename, ext_fname))
        return clean_filename

    def _ensure_unix_pathname(self, pathname):
        # it's only windows we have to worry about
        if self.platform != "win32":
            return pathname
        replace = re.compile(r"\\")
        fnm = re.sub(replace, "/", pathname)
        return fnm
