#!/usr/bin/env python

import ast
import re
from setuptools import setup, find_packages

DEPENDENCIES = [
    'boto3==1.2.2',
    'virtualenv',
]

TESTS_REQUIRE = [
    'pylint==1.4.1',
    'flake8==2.3.0',
    'pytest==2.8.2',
]


def package_meta():
    """Read __init__.py for global package metadata.
    Do this without importing the package.
    """
    _version_re = re.compile(r'__version__\s+=\s+(.*)')
    _url_re = re.compile(r'__url__\s+=\s+(.*)')
    _license_re = re.compile(r'__license__\s+=\s+(.*)')

    with open('lambda_uploader/__init__.py', 'rb') as ffinit:
        initcontent = ffinit.read()
        version = str(ast.literal_eval(_version_re.search(
            initcontent.decode('utf-8')).group(1)))
        url = str(ast.literal_eval(_url_re.search(
            initcontent.decode('utf-8')).group(1)))
        licencia = str(ast.literal_eval(_license_re.search(
            initcontent.decode('utf-8')).group(1)))
    return {
        'version': version,
        'license': licencia,
        'url': url,
    }

_lu_meta = package_meta()

setup(
    name='lambda-uploader',
    description='AWS Python Lambda Packager',
    keywords='aws lambda',
    version=_lu_meta['version'],
    tests_require=TESTS_REQUIRE,
    install_requires=DEPENDENCIES,
    packages=find_packages(exclude=['tests']),
    classifiers=[
        "Programming Language :: Python :: 2.7",
    ],
    license=_lu_meta['license'],
    author="Rackers",
    maintainer_email="jim.rosser@rackspace.com",
    url=_lu_meta['url'],
    entry_points={
        'console_scripts': [
            'lambda-uploader=lambda_uploader.shell:main'
        ]
    },
)
