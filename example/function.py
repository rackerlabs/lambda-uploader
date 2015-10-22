import boto3

print('Loading function')

s3 = boto3.client('s3')


def lambda_handler(event, context):
    print("Event: %s" % event)
