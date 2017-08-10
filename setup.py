#!/usr/bin/env python
"""
Setup module for trekipsum.
"""
from datetime import datetime

from setuptools import find_packages, setup

build_time = datetime.utcnow().strftime('%Y%m%d%H%M%S')

setup(
    name='trekipsum',
    version='1.0.{}'.format(build_time),
    long_description='Generates pseudo-random strings of text, like lorem ipsum, '
                     'based on dialog from Star Trek.',
    url='https://github.com/infinitewarp/trekipsum',
    author='Brad Smith',
    license='MIT',
    package_dir={'': 'trekipsum'},
    packages=find_packages('trekipsum', exclude=['scrape']),
    install_requires=[],
    dependency_links=[],
    zip_safe=True,
)
