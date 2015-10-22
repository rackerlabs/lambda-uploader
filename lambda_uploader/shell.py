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
EXCLAIM = '\xe2\x9d\x97\xef\xb8\x8f'
CHECK = '\xe2\x9c\x85'
PIZZA = '\xf0\x9f\x8d\x95'
INTERROBANG = '\xe2\x81\x89\xef\xb8\x8f'
RED_X = '\xe2\x9d\x8c'


def _execute(args):
    pth = path.abspath(args.function_dir)

    cfg = config.Config(pth)
    print("%s Building Package %s" % (PIZZA, PIZZA))
    package.build_package(pth, cfg.requirements)
    if not args.no_upload:
        print("%s Uploading Package %s" % (PIZZA, PIZZA))
        uploader.upload_package(pth, cfg)

    if not args.no_clean:
        package.cleanup(pth)

    print("%s Fin %s" % (PIZZA, PIZZA))


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
                        help='dont cleanup any files after uploading',
                        const=True)
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
