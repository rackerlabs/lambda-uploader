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
import zipfile
import logging
import sys
import re

from subprocess import Popen, PIPE
from lambda_uploader import utils
from distutils.spawn import find_executable

# Python 2/3 compatibility
try:
    basestring
except NameError:
    basestring = str


LOG = logging.getLogger(__name__)
TEMP_WORKSPACE_NAME = ".lambda_uploader_temp"
ZIPFILE_NAME = 'lambda_function.zip'


def build_package(path, requires, virtualenv=None, ignore=None,
                  extra_files=None, zipfile_name=ZIPFILE_NAME):
    '''Builds the zip file and creates the package with it'''
    pkg = Package(path, zipfile_name)

    if extra_files:
        for fil in extra_files:
            pkg.extra_file(fil)
    if virtualenv is not None:
        pkg.virtualenv(virtualenv)
    pkg.requirements(requires)
    pkg.build(ignore)

    return pkg


def create_package(path, zipfile_name=ZIPFILE_NAME):
    '''Creates the package with already existing zip file'''
    pkg = Package(path, zipfile_name)
    return pkg


class Package(object):
    def __init__(self, path, zipfile_name=ZIPFILE_NAME):
        self._path = path
        self._temp_workspace = os.path.join(path,
                                            TEMP_WORKSPACE_NAME)

        self.zip_file = os.path.join(path, zipfile_name)
        self._virtualenv = None
        self._skip_virtualenv = False
        self._requirements = None
        self._requirements_file = os.path.join(self._path, "requirements.txt")
        self._extra_files = []

    def build(self, ignore=None):
        '''Calls all necessary methods to build the Lambda Package'''
        self._prepare_workspace()
        self.install_dependencies()
        self.package(ignore)

    def clean_workspace(self):
        '''Clean up the temporary workspace if one exists'''
        if os.path.isdir(self._temp_workspace):
            shutil.rmtree(self._temp_workspace)

    def clean_zipfile(self):
        '''remove existing zipfile'''
        if os.path.isfile(self.zip_file):
            os.remove(self.zip_file)

    def requirements(self, requires):
        '''
        Sets the requirements for the package.

        It will take either a valid path to a requirements file or
        a list of requirements.
        '''
        if requires:
            if isinstance(requires, basestring) and \
               os.path.isfile(os.path.abspath(requires)):
                self._requirements_file = os.path.abspath(requires)
            else:
                if isinstance(self._requirements, basestring):
                    requires = requires.split()
                self._requirements_file = None
                self._requirements = requires
        else:
            # If the default requirements file is found use that
            if os.path.isfile(self._requirements_file):
                return
            self._requirements, self._requirements_file = None, None

    def virtualenv(self, virtualenv):
        '''
        Sets the virtual environment for the lambda package

        If this is not set then package_dependencies will create a new one.

        Takes a path to a virtualenv or a boolean if the virtualenv creation
        should be skipped.
        '''
        # If a boolean is passed then set the internal _skip_virtualenv flag
        if isinstance(virtualenv, bool):
            self._skip_virtualenv = virtualenv
        else:
            self._virtualenv = virtualenv
            if not os.path.isdir(self._virtualenv):
                raise Exception("virtualenv %s not found" % self._virtualenv)
            LOG.info("Using existing virtualenv at %s" % self._virtualenv)
            # use supplied virtualenv path
            self._pkg_venv = self._virtualenv
            self._skip_virtualenv = True

    def extra_file(self, element):
        '''
        Sets an additional file or path that we copy into the resulting package
        '''
        self._extra_files.append(element)

    def install_dependencies(self):
        ''' Creates a virtualenv and installs requirements '''
        # If virtualenv is set to skip then do nothing
        if self._skip_virtualenv:
            LOG.info('Skip Virtualenv set ... nothing to do')
            return

        has_reqs = _isfile(self._requirements_file) or self._requirements
        if self._virtualenv is None and has_reqs:
            LOG.info('Building new virtualenv and installing requirements')
            self._build_new_virtualenv()
            self._install_requirements()
        elif self._virtualenv is None and not has_reqs:
            LOG.info('No requirements found, so no virtualenv will be made')
            self._pkg_venv = False
        else:
            raise Exception('Cannot determine what to do about virtualenv')

    def _prepare_workspace(self):
        '''
        Remove existing workspace if it exists and/or create a new workspace
        '''
        # Wipe out existing workspace
        self.clean_workspace()
        # Setup temporary workspace
        os.mkdir(self._temp_workspace)

    def _build_new_virtualenv(self):
        '''Build a new virtualenvironment if self._virtualenv is set to None'''
        if self._virtualenv is None:
            # virtualenv was "None" which means "do default"
            self._pkg_venv = os.path.join(self._temp_workspace, 'venv')
            self._venv_pip = 'bin/pip'
            if sys.platform == 'win32' or sys.platform == 'cygwin':
                self._venv_pip = 'Scripts\pip.exe'

            proc = Popen(["virtualenv", "-p", _python_executable(),
                          self._pkg_venv], stdout=PIPE, stderr=PIPE)
            stdout, stderr = proc.communicate()
            LOG.debug("Virtualenv stdout: %s" % stdout)
            LOG.debug("Virtualenv stderr: %s" % stderr)

            if proc.returncode is not 0:
                raise Exception('virtualenv returned unsuccessfully')

        else:
            raise Exception('cannot build a new virtualenv when asked to omit')

    def _install_requirements(self):
        '''
        Create a new virtualenvironment and install requirements
        if there are any.
        '''
        if not hasattr(self, '_pkg_venv'):
            err = 'Must call build_new_virtualenv before install_requirements'
            raise Exception(err)

        cmd = None
        if self._requirements:
            LOG.debug("Installing requirements found %s in config"
                      % self._requirements)
            cmd = [os.path.join(self._pkg_venv, self._venv_pip),
                   'install'] + self._requirements

        elif _isfile(self._requirements_file):
            # Pip install
            LOG.debug("Installing requirements from requirements.txt file")
            cmd = [os.path.join(self._pkg_venv, self._venv_pip),
                   "install", "-r",
                   self._requirements_file]

        if cmd is not None:
            prc = Popen(cmd, stdout=PIPE, stderr=PIPE)
            stdout, stderr = prc.communicate()
            LOG.debug("Pip stdout: %s" % stdout)
            LOG.debug("Pip stderr: %s" % stderr)

            if prc.returncode is not 0:
                raise Exception('pip returned unsuccessfully')

    def package(self, ignore=None):
        """
        Create a zip file of the lambda script and its dependencies.

        :param list ignore: a list of regular expression strings to match paths
            of files in the source of the lambda script against and ignore
            those files when creating the zip file. The paths to be matched are
            local to the source root.
        """
        ignore = ignore or []
        package = os.path.join(self._temp_workspace, 'lambda_package')

        # Copy site packages into package base
        LOG.info('Copying site packages')

        if hasattr(self, '_pkg_venv') and self._pkg_venv:
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

        # Append the temp workspace to the ignore list:
        ignore.append(r"^%s/.*" % re.escape(TEMP_WORKSPACE_NAME))
        utils.copy_tree(self._path, package, ignore)

        # Add extra files
        for p in self._extra_files:
            LOG.info('Copying extra %s into package' % p)
            ignore.append(re.escape(p))
            if os.path.isdir(p):
                utils.copy_tree(p, package, ignore=ignore, include_parent=True)
            else:
                shutil.copy(p, package)

        self._create_zip(package)

    def _create_zip(self, src):
        LOG.info('Creating zipfile')
        zf = zipfile.ZipFile(self.zip_file, "w", zipfile.ZIP_DEFLATED)
        abs_src = os.path.abspath(src)
        for root, _, files in os.walk(src):
            for filename in files:
                absname = os.path.abspath(os.path.join(root, filename))
                arcname = absname[len(abs_src) + 1:]
                LOG.debug('Zipping %s as %s'
                          % (os.path.join(root, filename), arcname))

                zf.write(absname, arcname)
        zf.close()


def _isfile(path):
    """Variant of os.path.isfile that is somewhat type-resilient."""
    if not path:
        return False
    return os.path.isfile(path)


def _python_executable():
        python_exe = find_executable('python2')
        if not python_exe:
            python_exe = find_executable('python')

        if not python_exe:
            raise Exception('Unable to locate python executable')

        return python_exe
