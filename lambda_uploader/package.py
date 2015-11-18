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
import sys

from subprocess import Popen, PIPE
from lambda_uploader import utils

LOG = logging.getLogger(__name__)
TEMP_WORKSPACE_NAME = ".lamba_uploader_temp"
ZIPFILE_NAME = 'lambda_function.zip'


def build_package(path, requirements):
    pkg = Package(path)

    pkg.clean_workspace()
    pkg.clean_zipfile()
    pkg.prepare_workspace()
    pkg.install_requirements(requirements)
    pkg.package()
    return pkg


class Package(object):
    def __init__(self, path):
        self._path = path
        self._temp_workspace = os.path.join(path,
                                            TEMP_WORKSPACE_NAME)
        self.zip_file = os.path.join(path, ZIPFILE_NAME)

        self._pkg_venv = os.path.join(self._temp_workspace, 'venv')
        self._venv_pip = 'bin/pip'
        if sys.platform == 'win32' or sys.platform == 'cygwin':
            self._venv_pip = 'Scripts\pip.exe'

    def clean_workspace(self):
        if os.path.isdir(self._temp_workspace):
            shutil.rmtree(self._temp_workspace)

    def clean_zipfile(self):
        if os.path.isfile(self.zip_file):
            os.remove(self.zip_file)

    def prepare_workspace(self):
        # Setup temporary workspace
        os.mkdir(self._temp_workspace)

        proc = Popen(["virtualenv", self._pkg_venv], stdout=PIPE, stderr=PIPE)
        stdout, stderr = proc.communicate()
        LOG.debug("Virtualenv stdout: %s" % stdout)
        LOG.debug("Virtualenv stderr: %s" % stderr)

        if proc.returncode is not 0:
            raise Exception('virtualenv returned unsuccessfully')

    def install_requirements(self, requirements):
        cmd = None
        if requirements:
            LOG.debug("Installing requirements found %s in config"
                      % requirements)
            cmd = [os.path.join(self._pkg_venv, self._venv_pip),
                   'install'] + requirements

        elif os.path.isfile("requirements.txt"):
            # Pip install
            LOG.debug("Installing requirements from requirements.txt file")
            cmd = [os.path.join(self._pkg_venv, self._venv_pip),
                   "install", "-r", "requirements.txt"]

        if cmd is not None:
            prc = Popen(cmd, stdout=PIPE, stderr=PIPE)
            stdout, stderr = prc.communicate()
            LOG.debug("Pip stdout: %s" % stdout)
            LOG.debug("Pip stderr: %s" % stderr)

            if prc.returncode is not 0:
                raise Exception('pip returned unsuccessfully')

    def package(self):
        package = os.path.join(self._temp_workspace, 'lambda_package')

        # Copy site packages into package base
        LOG.info('Copying site packages')

        site_packages = 'lib/python2.7/site-packages'
        lib64_site_packages = 'lib64/python2.7/site-packages'
        if sys.platform == 'win32' or sys.platform == 'cygwin':
            lib64_site_packages = 'lib64\\site-packages'
            site_packages = 'lib\\site-packages'

        utils.copy_tree(os.path.join(self._pkg_venv, site_packages),
                        package)
        lib64_path = os.path.join(self._pkg_venv, lib64_site_packages)
        if not os.path.islink(lib64_path):
            LOG.info('Copying lib64 site packages')
            utils.copy_tree(lib64_path, package)

        utils.copy_tree(self._path, package, ignore=[TEMP_WORKSPACE_NAME])
        self._create_zip(package)

    def _create_zip(self, src):
        zfile = os.path.join(self._path, ZIPFILE_NAME)
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
