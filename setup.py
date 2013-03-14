#!/usr/bin/env python
from setuptools import setup, find_packages
execfile('src/cuisine_sweet/version.py')
setup(
    name = "cuisine_sweet",
    version = __version__,
    # pypi stuff
    author = "Dexter Tad-y",
    author_email = "dtady@cpan.org",
    description = "Sugar-coated declarative deployment recipes built on top of Fabric and Cuisine",
    license = "Revised BSD License",
    keywords = [ "fabric", "cuisine", "deployment" ],
    url = "http://github.com/dexterbt1/cuisine_sweet",

    packages = find_packages('src/'),
    package_dir = {
        '': 'src',
    },
    scripts = [],

    install_requires = [
        'Fabric',
        'PyYAML',
        'cuisine==0.3.2',
        'distribute',
        'docutils',
        'decorator',
        'pexpect',
    ],

    # could also include long_description, download_url, classifiers, etc.
    download_url = 'https://github.com/dexterbt1/cuisine_sweet/tarball/%s' % __version__,
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Natural Language :: English",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
    ],
)
