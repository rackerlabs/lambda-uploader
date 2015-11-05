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

import json
from os import path

REQUIRED_PARAMS = {'name': basestring, 'description': basestring,
                   'region': basestring, 'handler': basestring,
                   'role': basestring, 'timeout': int, 'memory': int}

DEFAULT_PARAMS = {u'requirements': [], u'publish': False}


class Config(object):
    def __init__(self, pth):
        self._path = pth
        self._config = None
        self._load_config()
        self._set_defaults()

        for param, clss in REQUIRED_PARAMS.iteritems():
            self._validate(param, cls=clss)

    @property
    def raw(self):
        if not self._config:
            self._load_config()

        return self._config

    def set_publish(self):
        self._config['publish'] = True

    def _set_defaults(self):
        for param, val in DEFAULT_PARAMS.iteritems():
            if self._config.get(param) is None:
                self._config[param] = val

    def _validate(self, key, cls=None):
        if key not in self._config:
            raise ValueError("Config %s must have %s set"
                             % (self._path, key))
            if cls:
                if not isinstance(self._config[key], cls):
                    raise TypeError("Config value '%s' should be %s not %s"
                                    % (key, cls, type(self._config[key])))

    def _load_config(self):
        config_file = path.join(self._path, 'lambda.json')
        if not path.isfile(config_file):
            raise Exception("lambda.json not found")

        with open(config_file) as config_file:
            self._config = json.load(config_file)

    def __getattr__(self, key):
        val = self._config.get(key)
        if val is not None:
            return val
        else:
            return object.__getattribute__(self, key)
