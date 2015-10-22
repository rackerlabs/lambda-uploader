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
import zipfile
import logging

from subprocess import Popen, PIPE

LOG = logging.getLogger(__name__)
TEMP_WORKSPACE_NAME = ".lambda_package"
ZIPFILE_NAME = 'lambda_function.zip'


def cleanup(path):
    temp_workspace = os.path.join(path, TEMP_WORKSPACE_NAME)
    if os.path.isdir(temp_workspace):
        shutil.rmtree(temp_workspace)
    zip_file = os.path.join(path, ZIPFILE_NAME)
    if os.path.isfile(zip_file):
        os.remove(zip_file)


def build_package(path, requirements=None):
    temp_workspace = os.path.join(path, TEMP_WORKSPACE_NAME)
    # Calling cleanup first to cover a previous failed run
    cleanup(path)

    # Setup temporary workspace
    os.mkdir(temp_workspace)

    pkg_venv = os.path.join(temp_workspace, 'venv')
    proc = Popen(["virtualenv", pkg_venv], stdout=PIPE, stderr=PIPE)
    stdout, stderr = proc.communicate()
    LOG.debug("Virtualenv stdout: %s" % stdout)
    LOG.debug("Virtualenv stderr: %s" % stderr)

    if proc.returncode is not 0:
        raise Exception('virtualenv returned unsuccessfully')

    cmd = None
    if requirements is not None:
        LOG.debug("Installing requirements found %s in config" % requirements)
        cmd = [os.path.join(pkg_venv, 'bin/pip'),
               'install', " ".join(requirements)]

    elif os.path.isfile("requirements.txt"):
        # Pip install
        LOG.debug("Installing requirements from requirements.txt file")
        cmd = [os.path.join(pkg_venv, 'bin/pip'),
               "install", "-r", "requirements.txt"]

    if cmd is not None:
        prc = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = prc.communicate()
        LOG.debug("Pip stdout: %s" % stdout)
        LOG.debug("Pip stderr: %s" % stderr)

        if proc.returncode is not 0:
            raise Exception('pip returned unsuccessfully')
    package = os.path.join(temp_workspace, 'lambda_package')

    # Copy site packages into package base
    LOG.info('Copying site packages')
    shutil.copytree(os.path.join(pkg_venv, 'lib/python2.7/site-packages'),
                    package)
    _copy_src_files(path, package)
    _create_zip(package, path)


def _copy_src_files(src, package):
    LOG.info('Copying source files')
    # Re-create cwd directory structure
    for root, subdirs, files in os.walk(src):
        for subdir in subdirs:
            subdir_path = os.path.join(root, subdir)
            if TEMP_WORKSPACE_NAME in subdir_path:
                continue
            fpath = os.path.join(package, subdir)
            LOG.debug("Creating directory %s" % fpath)
            os.mkdir(fpath)

        for filename in files:
            path = os.path.join(root, filename)
            if TEMP_WORKSPACE_NAME in path:
                continue

            shutil.copy(path, package)


def _create_zip(src, dest):
    zfile = os.path.join(dest, ZIPFILE_NAME)
    LOG.info('Creating zipfile')
    zf = zipfile.ZipFile(zfile, "w", zipfile.ZIP_DEFLATED)
    abs_src = os.path.abspath(src)
    for root, _, files in os.walk(src):
        for filename in files:
            absname = os.path.abspath(os.path.join(root, filename))
            arcname = absname[len(abs_src) + 1:]
            LOG.debug('Zipping %s as %s'
                      % (os.path.join(root, filename), arcname))

            zf.write(absname, arcname)
    zf.close()
