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

REQUIRED_PARAMS = {u'name': basestring, u'description': basestring,
                   u'region': basestring, u'handler': basestring,
                   u'role': basestring, u'timeout': int, u'memory': int}

DEFAULT_PARAMS = {u'requirements': [], u'publish': False,
                  u'alias': None, u'alias_description': None,
                  u'ignore': [], u'function_path': ''}


class Config(object):
    def __init__(self, pth, config_file=None, role=None):
        self._path = pth
        self._config = None
        self._load_config(config_file)
        if role is not None:
            self._config['role'] = role
        self._set_defaults()

        for param, clss in REQUIRED_PARAMS.iteritems():
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

    '''Set the publish attr to true'''
    def set_publish(self):
        self._config['publish'] = True

    '''Set the alias and description'''
    def set_alias(self, alias, description=None):
        self._config['alias'] = alias
        self._config['alias_description'] = description
        self._config['publish'] = True

    '''Set all defaults after loading the config'''
    def _set_defaults(self):
        for param, val in DEFAULT_PARAMS.iteritems():
            if self._config.get(param) is None:
                self._config[param] = val

    '''Validate the configuration file'''
    def _validate(self, key, cls=None):
        if key not in self._config:
            raise ValueError("Config %s must have %s set"
                             % (self._path, key))
            if cls:
                if not isinstance(self._config[key], cls):
                    raise TypeError("Config value '%s' should be %s not %s"
                                    % (key, cls, type(self._config[key])))

    '''Load config ... called by init()'''
    def _load_config(self, lambda_file=None):
        if not lambda_file:
            lambda_file = path.join(self._path, 'lambda.json')

        if not path.isfile(lambda_file):
            raise Exception("%s not found" % lambda_file)

        with open(lambda_file) as config_file:
            self._config = json.load(config_file)

    def __getattr__(self, key):
        val = self._config.get(key)
        if val is not None:
            return val
        else:
            return object.__getattribute__(self, key)
