from os import path
from lambda_uploader import config
import pytest

EX_CONFIG = path.normpath(path.join(path.dirname(__file__),
                          '../test/configs'))


def test_load_config():
    cfg = config.Config(EX_CONFIG)

    # Do a quick test of some attributes
    attrs = {'name': 'myFunc',
             'description': 'myfunc',
             'region': 'us-east-1'}

    for key, val in attrs.iteritems():
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
