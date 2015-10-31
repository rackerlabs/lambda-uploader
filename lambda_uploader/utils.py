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

import os
import shutil
import logging


LOG = logging.getLogger(__name__)


def copy_tree(src, dest, ignore=[]):
    LOG.info('Copying source files')
    # Re-create directory structure
    for root, _, files in os.walk(src):
        for filename in files:
            path = os.path.join(root, filename)
            if _ignore_file(path, ignore):
                continue

            sub_dirs = os.path.dirname(os.path.relpath(path,
                                                       start=src))
            pkg_path = os.path.join(dest, sub_dirs)
            if not os.path.isdir(pkg_path):
                os.makedirs(pkg_path)

            LOG.debug("Copying %s to %s" % (path, pkg_path))
            shutil.copy(path, pkg_path)


# Iterate through every item in ignore
# and check for matches in the path
def _ignore_file(path, ignore=[]):
    if not ignore:
        return False
    for ign in ignore:
        if ign in path:
            return True
    return False
