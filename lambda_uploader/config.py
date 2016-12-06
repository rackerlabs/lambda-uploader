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

import json
from os import path

# Python 2/3 compatability
try:
    basestring
except NameError:
    basestring = str

REQUIRED_PARAMS = {u'name': basestring, u'description': basestring,
                   u'region': basestring, u'handler': basestring,
                   u'role': basestring, u'timeout': int, u'memory': int}
REQUIRED_VPC_PARAMS = {u'subnets': list, u'security_groups': list}

DEFAULT_PARAMS = {u'requirements': [], u'publish': False,
                  u'alias': None, u'alias_description': None,
                  u'ignore': [], u'extra_files': [], u'vpc': None,
                  u's3_bucket': None, u's3_key': None, u'runtime': 'python2.7',
                  u'variables': {}}


class Config(object):
    def __init__(self, pth, config_file=None, role=None, variables=None):
        self._path = pth
        self._config = None
        self._load_config(config_file)
        if role is not None:
            self._config['role'] = role
        if variables is not None:
            self._config['variables'] = json.loads(variables)
        self._set_defaults()
        if self._config['vpc']:
            self._validate_vpc()

        for param, clss in REQUIRED_PARAMS.items():
            self._validate(param, cls=clss)

    '''
    Return raw config
    '''
    @property
    def raw(self):
        if not self._config:
            self._load_config()

        return self._config

    '''
    Return an alias description if set otherwise return an the function
    description
    '''
    @property
    def alias_description(self):
        if self._config['alias_description'] is None:
            return self._config['description']
        else:
            return self._config['alias_description']

    '''
    Public method to set the S3 bucket and keyname
    '''
    def set_s3(self, bucket, key=None):
        self._config['s3_bucket'] = bucket
        if key:
            self._config['s3_key'] = key

    '''Set the publish attr to true'''
    def set_publish(self):
        self._config['publish'] = True

    '''Set the alias and description'''
    def set_alias(self, alias, description=None):
        self._config['alias'] = alias
        self._config['alias_description'] = description
        self._config['publish'] = True

    '''Set the runtime '''
    def set_runtime(self, runtime):
        self._config['runtime'] = runtime

    '''Set all defaults after loading the config'''
    def _set_defaults(self):
        for param, val in DEFAULT_PARAMS.items():
            if self._config.get(param) is None:
                self._config[param] = val

    '''Validate the configuration file'''
    def _validate(self, key, cls=None):
        if key not in self._config:
            raise ValueError("Config %s must have %s set"
                             % (self._path, key))

        return self._compare(key, cls, self._config[key])

    '''Validate the VPC configuration'''
    def _validate_vpc(self):
        for param, clss in REQUIRED_VPC_PARAMS.items():
            self._compare(param, clss, self._config['vpc'].get(param))

            if len(self._config['vpc'].get(param)) == 0:
                raise TypeError("VPC Config '%s' should have at least"
                                " one item in its array!" % param)
            for value in self._config['vpc'].get(param):
                if not isinstance(value, basestring):
                    raise TypeError("VPC Config arrays can only contain"
                                    " strings. '%s' contains something else"
                                    % param)

    '''Compare if a string is a certain type'''
    def _compare(self, key, cls, value):
        if cls:
            if not isinstance(value, cls):
                raise TypeError("Config value '%s' should be %s not %s"
                                % (key, cls, type(value)))

    def s3_package_name(self):
        if self._config.get('s3_key'):
            return self.s3_key
        return self.name + '.zip'

    '''Load config ... called by init()'''
    def _load_config(self, lambda_file=None):
        if not path.isdir(self._path):
            raise Exception("%s not a valid function directory" % self._path)

        if not lambda_file:
            lambda_file = path.join(self._path, 'lambda.json')

        if not path.isfile(lambda_file):
            raise Exception("%s not a valid configuration file" % lambda_file)

        with open(lambda_file) as config_file:
            self._config = json.load(config_file)

    def __getattr__(self, key):
        if key in self._config:
            return self._config[key]
        else:
            return object.__getattribute__(self, key)
