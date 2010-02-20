import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name = 'pybagit',
    version = '1.0',
    url = 'http://www.musiclibs.net/pybagit',
    author = 'Andrew Hankinson',
    author_email = 'andrew.hankinson@mail.mcgill.ca',
    license = 'http://www.opensource.org/licenses/mit-license.php',
    packages = find_packages(),
    description = 'A library for dealing with BagIt packages.',
    test_suite = 'bagtest'
)