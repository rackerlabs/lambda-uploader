from os import path
from lambda_uploader import config

EX_CONFIG = path.normpath(path.join(path.dirname(__file__),
                          '../example'))


def test_load_config():
    cfg = config.Config(EX_CONFIG)

    # Do a quick test of some attributes
    attrs = {'name': 'myFunc',
             'description': 'myfunc',
             'region': 'us-east-1'}

    for key, val in attrs.iteritems():
        assert cfg.raw[key] == val


def test_set_publish():
    cfg = config.Config(EX_CONFIG)
    # Check that we default to false
    assert cfg.publish is False

    cfg.set_publish()
    assert cfg.publish
