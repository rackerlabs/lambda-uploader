# lambda-uploader

Provides a quick command line utility for packaging and publishing Python AWS Lambda
functions.  This is a work in progress and pull requests are always welcome.

### Installation
The latest release of lambda-uploader can be installed via pip:
```
pip install lambda-uploader
```
An alternative install method would be manually installing it leveraging `setup.py`:
```
git clone https://github.com/rackerlabs/lambda-uploader
cd lambda-uploader
python setup.py install
```

### Configuration File
The lambda uploader expects a directory with, at a minimum, your lambda function
and a lambda.json file.  It is not necessary to set requirements in your config
file since the lambda uploader will also check for and use a requirements.txt file.

Example lambda.json file:
```json
{
  "name": "myFunction",
  "description": "It does things",
  "region": "us-east-1",
  "handler": "function.lambda_handler",
  "role": "arn:aws:iam::00000000000:role/lambda_basic_execution",
  "requirements": ["pygithub"],
  "ignore": [
    "circle.yml",
    ".git",
    "/*.pyc"
  ],
  "timeout": 30,
  "memory": 512
}
```

### Command Line Usage
To package and upload simply run the command from within your lambda directory or
with the directory as an option.
```shell
lambda-uploader ./myfunc
```

To specify an alternative profile that has been defined in `~/.aws/credentials` use the
`--profile` parameter.
```shell
lambda-uploader --profile=alternative-profile
```

To specify an alternative, prexisting virtualenv use the `--virtualenv` parameter.
```shell
lambda-uploader --virtualenv=~/.virtualenv/my_custom_virtualenv
```

To omit using a virtualenv use the `--no-virtualenv` parameter.
```shell
lambda-uploader --no-virtualenv
```

If you would prefer to upload another way you can tell the uploader to ignore the upload.
This will create a package and leave it in the project directory.
```shell
lambda-uploader --no-upload ./myfunc
```

To publish a version without an alias you would pass the the publish flag.
```shell
lambda-uploader -p ./myfunc
```

If you would like to alias your upload you can pass the alias with the alias flag. The
function description will be used when an alias-description is not provided.
```shell
lambda-uploader --alias myAlias --alias-description 'My alias description' ./myfunc
```
