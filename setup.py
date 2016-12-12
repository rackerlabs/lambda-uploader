#!/usr/bin/env python

import ast
import re
from setuptools import setup, find_packages

INSTALL_REQUIRES = [
    'boto3>=1.4.2',
    'botocore>=1.4.85',
    'virtualenv',
]

STYLE_REQUIRES = [
    'flake8>=2.5.4',
    'pylint>=1.5.5',
]


TEST_REQUIRES = [
    'coverage>=4.0.3',
    'pytest>=2.9.1',
    'moto>=0.4.23',
]


EXTRAS_REQUIRE = {
    'test': TEST_REQUIRES,
    'style': STYLE_REQUIRES,
    # alias
    'lint': STYLE_REQUIRES,
    'test-requirements': TEST_REQUIRES + STYLE_REQUIRES,
}


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
    extras_require=EXTRAS_REQUIRE,
    tests_require=TEST_REQUIRES + STYLE_REQUIRES,
    install_requires=INSTALL_REQUIRES,
    packages=find_packages(exclude=['tests']),
    test_suite='tests',
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
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
