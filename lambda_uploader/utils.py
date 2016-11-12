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

import os
import shutil
import logging
import re


LOG = logging.getLogger(__name__)


def copy_tree(src, dest, ignore=None, include_parent=False):
    ignore = ignore or []
    if os.path.isfile(src):
        raise Exception('Cannot use copy_tree with a file as the src')

    LOG.info('Copying source files')
    if include_parent:
        # if src is foo, make dest/foo and copy files there
        nested_dest = os.path.normpath(
                os.path.join(dest, os.path.basename(src)))
        if not os.path.isdir(nested_dest):
            os.makedirs(nested_dest)
    else:
        nested_dest = dest

    # Re-create directory structure
    for root, _, files in os.walk(src):
        for filename in files:
            path = os.path.join(root, filename)
            path_relative_to_the_source_dir = os.path.relpath(path, src)
            if _ignore_file(path_relative_to_the_source_dir, ignore):
                continue

            sub_dirs = os.path.dirname(os.path.relpath(path,
                                                       start=src))
            pkg_path = os.path.join(nested_dest, sub_dirs)
            if not os.path.isdir(pkg_path):
                os.makedirs(pkg_path)

            LOG.debug("Copying %s to %s" % (path, pkg_path))
            shutil.copy(path, pkg_path)


# Iterate through every item in ignore
# and check for matches in the path
def _ignore_file(path, ignore=None):
    ignore = ignore or []
    if not ignore:
        return False
    for ign in ignore:
        if re.search(ign, path):
            return True
    return False
