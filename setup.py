#!/usr/bin/env python
# encoding: utf-8

import os
import sys

from setuptools import setup, find_packages


if sys.version_info < (2, 6):
    raise SystemExit("Python 2.6 or later is required.")

exec(open(os.path.join("marrow", "norm", "release.py")))



setup(
        name="marrow.norm",
        version=version,
        
        description="A loose object document mapper for MongoDB and Python.",
        long_description = """\
For full documentation, see the README.textile file present in the package,
or view it online on the GitHub project page:

https://github.com/lesite/marrow.norm""",
        
        author = "Le Site Inc.",
        author_email = "amcgregor@lesite.ca",
        url = "https://github.com/lesite/marrow.norm",
        license = "LGPL",
        
        install_requires = [
            'marrow.util < 2.0'
        ],
        
        test_suite = 'nose.collector',
        tests_require = [
            'nose',
            'coverage'
        ],
        
        classifiers = [
            "Development Status :: 1 - Planning",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: LGPL License",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2.6",
            "Programming Language :: Python :: 2.7",
            # "Programming Language :: Python :: 3",
            # "Programming Language :: Python :: 3.1",
            # "Programming Language :: Python :: 3.2",
            "Topic :: Software Development :: Libraries :: Python Modules"
        ],
        
        packages = find_packages(exclude=['examples', 'tests']),
        zip_safe = True,
        include_package_data = True,
        package_data = {'': ['README.textile', 'LICENSE']},
        
        namespace_packages = ['marrow'],
    )