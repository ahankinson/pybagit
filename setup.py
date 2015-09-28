try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

longdesc = """
PyBagIt Version 1.5

This module helps with creating an managing BagIt-compliant packages. It has
been created to conform to BagIt v0.96.

Documentation is available at http://ahankinson.github.io/pybagit.
Code hosting is available on GitHub at http://github.com/ahankinson/pybagit/.

Requirements
------------
Tested with Python 2.6+ (2.5 or lower will not work.)
No external modules required.
Module has not been tested on Windows.


Running Tests
-------------
There are a number of unit tests written to verify that this module functions
as expected. To run this, simply type

python setup.py test

in the package directory. NOTE: You will need a network connection to verify
the 'fetch' tests. If you don't have a network connection you can skip these
tests by commenting them out in 'bagtest.py'


Setup and Install
-----------------
To install this module, simply run:

python setup.py install

You can also install it with easy_install:

easy_install pybagit

(you may need to run these commands as a privileged user, e.g. 'sudo')

"""


setup(
    name = 'pybagit',
    long_description = longdesc,
    version = '1.5.2',
    url = 'http://ahankinson.github.io/pybagit',
    author = 'Andrew Hankinson',
    author_email = 'andrew.hankinson@mail.mcgill.ca',
    license = 'http://www.opensource.org/licenses/mit-license.php',
    packages = find_packages(exclude=['ez_setup']),
    classifiers = [ 'Development Status :: 5 - Production/Stable',
                    'Intended Audience :: Information Technology',
                    'License :: OSI Approved :: MIT License',
                    'Operating System :: OS Independent',
                    'Topic :: Internet',
                    'Topic :: Software Development :: Libraries',
                    'Topic :: System :: Archiving :: Packaging'
                    ],
    include_package_data=True,
    description = 'A library for dealing with BagIt packages.',
    test_suite = 'bagtest'
)
