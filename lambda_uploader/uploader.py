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

import boto3
import logging

LOG = logging.getLogger(__name__)


def upload_package(pkg, config):
    with open(pkg.zip_file, "rb") as fil:
        zip_file = fil.read()

    client = boto3.client('lambda', region_name=config.region)
    # Assume the function already exists in AWS
    existing_function = True

    try:
        get_resp = client.get_function_configuration(FunctionName=config.name)
        LOG.debug("AWS get_function_configuration response: %s" % get_resp)
    except:
        existing_function = False
        LOG.debug("function not found creating new function")

    if existing_function:
        LOG.debug('running update_function_code')
        response = client.update_function_code(
            FunctionName=config.name,
            ZipFile=zip_file,
            Publish=config.publish,
        )
        LOG.debug("AWS update_function_code response: %s" % response)
        LOG.debug('running update_function_configuration')
        response = client.update_function_configuration(
            FunctionName=config.name,
            Handler=config.handler,
            Role=config.role,
            Description=config.description,
            Timeout=config.timeout,
            MemorySize=config.memory,
        )
        LOG.debug("AWS update_function_configuration response: %s" % response)
    else:
        LOG.debug('running create_function_code')
        response = client.create_function(
            FunctionName=config.name,
            Runtime='python2.7',
            Handler=config.handler,
            Role=config.role,
            Code={'ZipFile': zip_file},
            Description=config.description,
            Timeout=config.timeout,
            MemorySize=config.memory,
            Publish=config.publish,
        )
        LOG.debug("AWS create_function response: %s" % response)

