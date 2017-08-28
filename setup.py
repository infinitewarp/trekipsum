#!/usr/bin/env python
"""
Setup module for trekipsum.
"""
from datetime import datetime

from setuptools import find_packages, setup

build_time = datetime.utcnow().strftime('%Y%m%d%H%M%S')

setup(
    name='trekipsum',
    version='1.0.0.dev1+{}'.format(build_time),
    long_description='Generates pseudo-random strings of text, like lorem ipsum, '
                     'based on dialog from Star Trek.',
    url='https://github.com/infinitewarp/trekipsum',
    author='Brad Smith',
    license='MIT',
    packages=find_packages(exclude=['tests']),
    package_data={
        'trekipsum': ['assets/*.pickle'],
    },
    install_requires=['six'],
    dependency_links=[],
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'trekipsum = trekipsum:main_cli',
        ],
    }
)
