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

import boto3
import logging

from os import path

LOG = logging.getLogger(__name__)
MAX_PACKAGE_SIZE = 50000000


class PackageUploader(object):
    def __init__(self, config, profile_name):
        self._config = config
        session = boto3.session.Session(region_name=config.region,
                                        profile_name=profile_name)
        self._client = session.client('lambda')
        self.version = None

    '''
    Calls the AWS methods to upload an existing package and update
    the function configuration

    returns the package version
    '''
    def upload_existing(self, pkg):
        self._validate_package_size(pkg.zipfile)
        with open(pkg.zip_file, "rb") as fil:
            zip_file = fil.read()

        LOG.debug('running update_function_code')
        conf_update_resp = self._client.update_function_code(
            FunctionName=self._config.name,
            ZipFile=zip_file,
            Publish=False,
        )
        LOG.debug("AWS update_function_code response: %s"
                  % conf_update_resp)
        LOG.debug('running update_function_configuration')
        response = self._client.update_function_configuration(
            FunctionName=self._config.name,
            Handler=self._config.handler,
            Role=self._config.role,
            Description=self._config.description,
            Timeout=self._config.timeout,
            MemorySize=self._config.memory,
        )
        LOG.debug("AWS update_function_configuration response: %s"
                  % response)

        version = response.get('Version')
        # Publish the version after upload and config update if needed
        if self._config.publish:
            resp = self._client.publish_version(
                    FunctionName=self._config.name,
                    )
            LOG.debug("AWS publish_version response: %s" % resp)
            version = resp.get('Version')

        return version

    '''
    Creates and uploads a new lambda function

    returns the package version
    '''
    def upload_new(self, pkg):
        self._validate_package_size(pkg.zipfile)
        with open(pkg.zip_file, "rb") as fil:
            zip_file = fil.read()

        LOG.debug('running create_function_code')
        response = self._client.create_function(
            FunctionName=self._config.name,
            Runtime='python2.7',
            Handler=self._config.handler,
            Role=self._config.role,
            Code={'ZipFile': zip_file},
            Description=self._config.description,
            Timeout=self._config.timeout,
            MemorySize=self._config.memory,
            Publish=self._config.publish,
        )
        LOG.debug("AWS create_function response: %s" % response)

        return response.get('Version')

    '''
    Auto determines whether the function exists or not and calls
    the appropriate method (upload_existing or upload_new).
    '''
    def upload(self, pkg):
        existing_function = True
        try:
            get_resp = self._client.get_function_configuration(
                    FunctionName=self._config.name)
            LOG.debug("AWS get_function_configuration response: %s" % get_resp)
        except:
            existing_function = False
            LOG.debug("function not found creating new function")

        if existing_function:
            self.version = self.upload_existing(pkg)
        else:
            self.version = self.upload_new(pkg)

    '''
    Create/update an alias to point to the package. Raises an
    exception if the package has not been uploaded.
    '''
    def alias(self):
        # if self.version is still None raise exception
        if self.version is None:
            raise Exception('Must upload package before applying alias')

        if self._alias_exists():
            self._update_alias()
        else:
            self._create_alias()

    '''
    Pulls down the current list of aliases and checks to see if
    an alias exists.
    '''
    def _alias_exists(self):
        resp = self._client.list_aliases(
                FunctionName=self._config.name)

        for alias in resp.get('Aliases'):
            if alias.get('Name') == self._config.alias:
                return True
        return False

    '''Creates alias'''
    def _create_alias(self):
        LOG.debug("Creating new alias %s" % self._config.alias)
        resp = self._client.create_alias(
                FunctionName=self._config.name,
                Name=self._config.alias,
                FunctionVersion=self.version,
                Description=self._config.alias_description,
                )
        LOG.debug("AWS create_alias response: %s" % resp)

    '''Update alias'''
    def _update_alias(self):
        LOG.debug("Updating alias %s" % self._config.alias)
        resp = self._client.update_alias(
                FunctionName=self._config.name,
                Name=self._config.alias,
                FunctionVersion=self.version,
                Description=self._config.alias_description,
                )
        LOG.debug("AWS update_alias response: %s" % resp)

    def _validate_package_size(self, pkg):
        '''
        Logs a warning if the package size is over the current max package size
        '''
        if path.getsize(pkg) > MAX_PACKAGE_SIZE:
            LOG.warning("Size of your deployment package is larger than 50MB!")
