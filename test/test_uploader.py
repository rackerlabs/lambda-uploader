import boto3

from os import path
from lambda_uploader import uploader, config
from moto import mock_s3

EX_CONFIG = path.normpath(path.join(path.dirname(__file__),
                          '../test/configs'))


@mock_s3
def test_s3_upload():
    mock_bucket = 'mybucket'
    conn = boto3.resource('s3')
    conn.create_bucket(Bucket=mock_bucket)

    conf = config.Config(path.dirname(__file__),
                         config_file=path.join(EX_CONFIG, 'lambda.json'))
    conf.set_s3(mock_bucket)
    upldr = uploader.PackageUploader(conf, None)

    upldr._upload_s3(path.join(path.dirname(__file__), 'dummyfile'))

    # fetch the contents back out, be sure we truly uploaded the dummyfile
    retrieved_bucket = conn.Object(
        mock_bucket,
        conf.s3_package_name()
        ).get()['Body']
    found_contents = str(retrieved_bucket.read()).rstrip()
    assert found_contents == 'dummy data'
