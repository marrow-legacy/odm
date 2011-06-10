#!/usr/bin/env python
# encoding: utf-8

import sys
import os

from setuptools import setup, find_packages


if sys.version_info < (2, 6):
    raise SystemExit("Python 2.6 or later is required.")

exec(open(os.path.join("marrow", "norm", "release.py")).read())


setup(
    name="marrow.mailer",
    version=version,
    
    description="""""",
    author="Alice Bevan-McGregor",
    author_email="alice+marrow@gothcandy.com",
    url="",
    download_url="",
    license="LGPL",
    keywords="",
    
    install_requires=["marrow.util"],
    
    test_suite="nose.collector",
    tests_require=["nose", "coverage"],
    
    classifiers=[
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
    
    packages=find_packages(exclude=["examples", "tests"]),
    zip_safe=True,
    include_package_data=True,
    package_data={
        "": ["README.textile", "LICENSE"]
    },
    
    namespace_packages=["marrow"],
    entry_points = {
    }
)