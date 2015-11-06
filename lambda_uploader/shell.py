# -*- coding: utf-8 -*-
# Copyright 2015 Rackspace US, Inc.
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

from os import getcwd, path
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

    cfg = config.Config(pth)

    _print('Building Package')
    pkg = package.build_package(pth, cfg.requirements)

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
    import argparse

    parser = argparse.ArgumentParser(
            version=('version %s' % lambda_uploader.__version__),
            description='Simple way to create and upload python lambda jobs')

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
    parser.add_argument('--profile', dest='profile',
                        help='specify AWS cli profile')
    alias_help = 'alias for published version (WILL SET THE PUBLISH FLAG)'
    parser.add_argument('--alias', '-a', dest='alias',
                        default=None, help=alias_help)
    parser.add_argument('--alias-description', '-m', dest='alias_description',
                        default=None, help='alias description')
    parser.add_argument('function_dir', default=getcwd(), nargs='?',
                        help='lambda function directory')

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
