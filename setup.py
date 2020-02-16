#!/usr/bin/env python3
from codecs import open
from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pycoolmaster",
    version="0.1.4",
    description="Lightweight Python API for older (RS232-only) CoolMaster HVAC bridges",
    long_description=long_description,
    author="Issac Goldstand",
    author_email="margol@beamartyr.net",
    url="http://github.com/issacg/pycoolmaster",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
        "Topic :: Home Automation",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=[],
    zip_safe=True,
    keywords="hvac homeautomation",
)
