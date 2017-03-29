from os import path
from lambda_uploader import config
import pytest

EX_CONFIG = path.normpath(path.join(path.dirname(__file__),
                          '../tests/configs'))


def test_load_config():
    cfg = config.Config(EX_CONFIG)

    # Do a quick test of some attributes
    attrs = {'name': 'myFunc',
             'description': 'myfunc',
             'region': 'us-east-1'}

    for key, val in attrs.items():
        assert cfg.raw[key] == val


def test_role_override():
    role = 'arn:aws:iam::00000000000:role/myfunc_role'
    cfg = config.Config(EX_CONFIG, role=role)

    assert cfg.role is role


def test_vpc_config():
    subnet = 'subnet-00000000'
    securitygroup = 'sg-00000000'
    vpc = {
        'subnets': [
            subnet
        ],
        'security_groups': [
            securitygroup
        ]
    }
    cfg = config.Config(EX_CONFIG)

    assert cfg.raw['vpc']['security_groups'][0] == vpc['security_groups'][0]
    assert cfg.raw['vpc']['subnets'][0] == vpc['subnets'][0]


def test_no_vpc():
    cfg = config.Config(EX_CONFIG, EX_CONFIG + '/lambda-no-vpc.json')

    assert cfg.raw['vpc'] is None


def test_kinesis_subscription():
    ksub = {
        'stream': 'arn:aws:kinesis:eu-west-1:000000000000:stream/services',
        'batch_size': 10
    }
    cfg = config.Config(EX_CONFIG, EX_CONFIG + '/lambda-with-subscription.json')
    assert cfg.raw['subscription']['kinesis']['stream'] == ksub['stream']
    assert cfg.raw['subscription']['kinesis']['batch_size'] == ksub['batch_size']


def test_kinesis_subscription_with_starting_position_at_timestamp():
    ksub = {
        'stream': 'arn:aws:kinesis:eu-west-1:000000000000:stream/services',
        'batch_size': 10,
        'starting_position_timestamp': '2017-11-01T11:00:00Z'
    }
    cfg = config.Config(EX_CONFIG, EX_CONFIG + '/lambda-with-subscription_at_ts.json')
    assert cfg.raw['subscription']['kinesis']['stream'] == ksub['stream']
    assert cfg.raw['subscription']['kinesis']['batch_size'] == ksub['batch_size']
    assert cfg.raw['subscription']['kinesis']['starting_position_timestamp'] == ksub['starting_position_timestamp']


def test_kinesis_subscription_with_starting_position_at_timestamp_fails_when_timestamp_is_invalid():
    with pytest.raises(Exception):
        cfg = config.Config(EX_CONFIG, EX_CONFIG + '/lambda-with-subscription_at_ts_invalid_ts.json')


def test_kinesis_subscription_with_starting_position_at_timestamp_fails_when_timestamp_not_provided():
    with pytest.raises(Exception):
        cfg = config.Config(EX_CONFIG, EX_CONFIG + '/lambda-with-subscription_at_ts_not_provided.json')


def test_set_publish():
    cfg = config.Config(EX_CONFIG)
    # Check that we default to false
    assert cfg.publish is False

    cfg.set_publish()
    assert cfg.publish


def test___getattr__():
    cfg = config.Config(EX_CONFIG, path.join(EX_CONFIG, 'lambda.json'))
    assert cfg.s3_bucket is None
    assert cfg.name == 'myFunc'


def test_invalid_config_as_dir():
    # pass the function directory as the lambda configuration --
    # this should not work!
    with pytest.raises(Exception):
        config.Config(EX_CONFIG, EX_CONFIG)


def test_invalid_config_missing_file():
    # try invalid file
    with pytest.raises(Exception):
        config.Config(EX_CONFIG, path.join(EX_CONFIG, 'pleasedontexist.json'))


def test_invalid_config_missing_function_dir():
    # try invalid file
    with pytest.raises(Exception):
        config.Config(path.join(EX_CONFIG, 'pleasedontexist_dir'))


def test_invalid_config_missing_function_dir2():
    with pytest.raises(Exception):
        config.Config(
            # invalid function dir
            path.join(EX_CONFIG, 'pleasedontexist_dir'),
            # valid config file
            path.join(EX_CONFIG, 'lambda.json')
        )


def test_default_runtime():
    cfg = config.Config(EX_CONFIG)
    assert cfg.runtime == 'python2.7'

    cfg.set_runtime('java8')
    assert cfg.runtime == 'java8'
