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

LOG = logging.getLogger(__name__)
TEMP_WORKSPACE_NAME = ".lambda_package"
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
                   'install', " ".join(requirements)]

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
        if sys.platform == 'win32' or sys.platform == 'cygwin':
            site_packages = 'lib\\site-packages'

        shutil.copytree(os.path.join(self._pkg_venv, site_packages),
                        package)
        self._copy_src_files(package)
        self._create_zip(package)

    def _copy_src_files(self, package):
        LOG.info('Copying source files')
        # Re-create cwd directory structure
        for root, subdirs, files in os.walk(self._path):
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
