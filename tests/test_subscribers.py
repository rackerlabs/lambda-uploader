from os import path
from mock import patch, Mock
import nose.tools as nt

from lambda_uploader import subscribers, config


EX_CONFIG = path.normpath(path.join(path.dirname(__file__),
                          '../tests/configs'))

class TestKinesisSubscriber(object):

    @patch('lambda_uploader.subscribers.boto3.session.Session')
    def test_successfully_adds_kinesis_subscription(self, mocked_session):
        _mocked_lambda = Mock()
        _mocked_session = Mock()
        _mocked_session.client = Mock()
        _mocked_session.client.return_value = _mocked_lambda
        mocked_session.return_value = _mocked_session
        conf = config.Config(path.dirname(__file__),
                             config_file=path.join(EX_CONFIG, 'lambda-with-subscription.json'))
        subscribers.create_subscriptions(conf, None)
        nt.assert_equals(True, _mocked_lambda.create_event_source_mapping.called)
