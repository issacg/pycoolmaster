#!/usr/bin/env python3
from codecs import open
from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))


setup(
    name="pycoolmaster",
    version="0.2.3",
    description="Lightweight Python API for older (RS232-only) CoolMaster HVAC bridges",
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
    install_requires=[
        "pyserial"
    ],
    zip_safe=True,
    keywords="hvac homeautomation",
)
