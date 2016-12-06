# -*- coding: utf-8 -*-
# Copyright 2015-2016 Rackspace US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""lambda-uploader - Simple way to create and upload python lambda jobs"""

from __future__ import print_function

import sys
import logging
import traceback
import lambda_uploader

from os import getcwd, path, getenv
from lambda_uploader import package, config, uploader

LOG = logging.getLogger(__name__)

NAMESPACE = 'rax_jira'
CHECK = '\xe2\x9c\x85'
INTERROBANG = '\xe2\x81\x89\xef\xb8\x8f'
RED_X = '\xe2\x9d\x8c'
LAMBDA = '\xce\xbb'


# Used for stdout for shell
def _print(txt):
    # Windows Powershell doesn't support Unicode
    if sys.platform == 'win32' or sys.platform == 'cygwin':
        print(txt)
    else:
        # Add the lambda symbol
        print("%s %s" % (LAMBDA, txt))


def _execute(args):
    pth = path.abspath(args.function_dir)

    cfg = config.Config(pth, args.config, role=args.role,
                        variables=args.variables)

    if args.s3_bucket:
        cfg.set_s3(args.s3_bucket, args.s3_key)

    if args.no_virtualenv:
        # specified flag to omit entirely
        venv = False
    elif args.virtualenv:
        # specified a custom virtualenv
        venv = args.virtualenv
    else:
        # build and include virtualenv, the default
        venv = None

    if args.no_build:
        pkg = package.create_package(pth)
    else:
        _print('Building Package')
        requirements = cfg.requirements
        if args.requirements:
            requirements = path.abspath(args.requirements)
        extra_files = cfg.extra_files
        if args.extra_files:
            extra_files = args.extra_files
        pkg = package.build_package(pth, requirements,
                                    venv, cfg.ignore, extra_files)

    if not args.no_clean:
        pkg.clean_workspace()

    if not args.no_upload:
        # Set publish if flagged to do so
        if args.publish:
            cfg.set_publish()

        create_alias = False
        # Set alias if the arg is passed
        if args.alias is not None:
            cfg.set_alias(args.alias, args.alias_description)
            create_alias = True

        _print('Uploading Package')
        upldr = uploader.PackageUploader(cfg, args.profile)
        upldr.upload(pkg)
        # If the alias was set create it
        if create_alias:
            upldr.alias()

        pkg.clean_zipfile()

    _print('Fin')


def main(arv=None):
    """lambda-uploader command line interface."""
    # Check for Python 2.7 or later
    if sys.version_info[0] < 3 and not sys.version_info[1] == 7:
        raise RuntimeError('lambda-uploader requires Python 2.7 or later')

    import argparse

    parser = argparse.ArgumentParser(
            description='Simple way to create and upload python lambda jobs')

    parser.add_argument('--version', '-v', action='version',
                        version=lambda_uploader.__version__)
    parser.add_argument('--no-upload', dest='no_upload',
                        action='store_const', help='dont upload the zipfile',
                        const=True)
    parser.add_argument('--no-clean', dest='no_clean',
                        action='store_const',
                        help='dont cleanup the temporary workspace',
                        const=True)
    parser.add_argument('--publish', '-p', dest='publish',
                        action='store_const',
                        help='publish an upload to an immutable version',
                        const=True)
    parser.add_argument('--virtualenv', '-e',
                        help='use specified virtualenv instead of making one',
                        default=None)
    parser.add_argument('--extra-files', '-x',
                        action='append',
                        help='include file or directory path in package',
                        default=[])
    parser.add_argument('--no-virtualenv', dest='no_virtualenv',
                        action='store_const',
                        help='do not create or include a virtualenv at all',
                        const=True)
    parser.add_argument('--role', dest='role',
                        default=getenv('LAMBDA_UPLOADER_ROLE'),
                        help=('IAM role to assign the lambda function, '
                              'can be set with $LAMBDA_UPLOADER_ROLE'))
    parser.add_argument('--variables', dest='variables',
                        help='add environment variables')
    parser.add_argument('--profile', dest='profile',
                        help='specify AWS cli profile')
    parser.add_argument('--requirements', '-r', dest='requirements',
                        help='specify a requirements.txt file')
    alias_help = 'alias for published version (WILL SET THE PUBLISH FLAG)'
    parser.add_argument('--alias', '-a', dest='alias',
                        default=None, help=alias_help)
    parser.add_argument('--alias-description', '-m', dest='alias_description',
                        default=None, help='alias description')
    parser.add_argument('--s3-bucket', '-s', dest='s3_bucket',
                        help='S3 bucket to store the lambda function in',
                        default=None)
    parser.add_argument('--s3-key', '-k', dest='s3_key',
                        help='Key name of the lambda function s3 object',
                        default=None)
    parser.add_argument('--config', '-c', help='Overrides lambda.json',
                        default='lambda.json')
    parser.add_argument('function_dir', default=getcwd(), nargs='?',
                        help='lambda function directory')
    parser.add_argument('--no-build', dest='no_build',
                        action='store_const', help='dont build the sourcecode',
                        const=True)

    verbose = parser.add_mutually_exclusive_group()
    verbose.add_argument('-V', dest='loglevel', action='store_const',
                         const=logging.INFO,
                         help="Set log-level to INFO.")
    verbose.add_argument('-VV', dest='loglevel', action='store_const',
                         const=logging.DEBUG,
                         help="Set log-level to DEBUG.")
    parser.set_defaults(loglevel=logging.WARNING)

    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    try:
        _execute(args)
    except Exception:
        print('%s Unexpected error. Please report this traceback.'
              % INTERROBANG, file=sys.stderr)

        traceback.print_exc()
        sys.stderr.flush()
        sys.exit(1)
