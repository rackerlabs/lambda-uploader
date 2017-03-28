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
import botocore
import logging
from datetime import datetime

LOG = logging.getLogger(__name__)


class KinesisSubscriber(object):
    ''' Invokes the lambda function on events from the Kinesis streams '''
    def __init__(self, config, profile_name,
                 function_name, stream_name, batch_size,
                 starting_position, starting_position_ts=None):
        self._aws_session = boto3.session.Session(region_name=config.region,
                                                  profile_name=profile_name)
        self._lambda_client = self._aws_session.client('lambda')
        self.function_name = function_name
        self.stream_name = stream_name
        self.batch_size = batch_size
        self.starting_position = starting_position
        self.starting_position_ts = starting_position_ts

    def subscribe(self):
        ''' Subscribes the lambda to the Kinesis stream '''
        try:
            LOG.debug('Creating Kinesis subscription')
            if self.starting_position_ts:
                self._lambda_client \
                    .create_event_source_mapping(
                            EventSourceArn=self.stream_name,
                            FunctionName=self.function_name,
                            BatchSize=self.batch_size,
                            StartingPosition=self.starting_position,
                            StartingPositionTimestamp=self.starting_position_ts)
            else:
                self._lambda_client \
                    .create_event_source_mapping(
                            EventSourceArn=self.stream_name,
                            FunctionName=self.function_name,
                            BatchSize=self.batch_size,
                            StartingPosition=self.starting_position)
            LOG.debug('Subscription created')
        except botocore.exceptions.ClientError as ex:
            response_code = ex.response['Error']['Code']
            if response_code == 'ResourceConflictException':
                LOG.debug('Subscription exists')
            else:
                LOG.error('Subscription failed, error=%s' % str(ex))
                raise ex


def create_subscriptions(config, profile_name):
    ''' Adds supported subscriptions '''
    if 'kinesis' in config.subscription.keys():
        data = config.subscription['kinesis']
        function_name = config.name
        stream_name = data['stream']
        batch_size = data['batch_size']
        starting_position = data['starting_position']
        starting_position_ts = None
        if starting_position == 'AT_TIMESTAMP':
            ts = data.get('starting_position_timestamp')
            starting_position_ts = datetime.strptime(ts, '%Y-%m-%dT%H:%M:%SZ')
        s = KinesisSubscriber(config, profile_name,
                              function_name, stream_name, batch_size,
                              starting_position,
                              starting_position_ts=starting_position_ts)
        s.subscribe()
