lambda-uploader
===============

Provides a quick command line utility for packaging and publishing
Python AWS Lambda functions. This is a work in progress and pull
requests are always welcome.

Installation
~~~~~~~~~~~~

The latest release of lambda-uploader can be installed via pip:

::

    pip install lambda-uploader

An alternative install method would be manually installing it leveraging
``setup.py``:

::

    git clone https://github.com/rackerlabs/lambda-uploader
    cd lambda-uploader
    python setup.py install

Configuration File
~~~~~~~~~~~~~~~~~~

The lambda uploader expects a directory with, at a minimum, your lambda
function and a ``lambda.json`` file. It is not necessary to set
requirements in your config file since the lambda uploader will also
check for and use a requirements.txt file.

Please note that you can leave the ``vpc`` object out of your config if
you want your lambda function to use your default VPC and subnets. If
you wish to use your lambda function inside a specific VPC, make sure
you set up the role correctly to allow this.

Note also the ``ignore`` entry is an array of regular expression strings
used to match against the relative paths - be careful to quote
accordingly. For example, a traditional ``*.txt`` "glob" is matched by
the JSON string: ``".*\\.txt$"`` (or just ``"\\.txt$"``).

Example ``lambda.json`` file:

.. code:: json

    {
      "name": "myFunction",
      "description": "It does things",
      "region": "us-east-1",
      "runtime": "python2.7",
      "handler": "function.lambda_handler",
      "role": "arn:aws:iam::00000000000:role/lambda_basic_execution",
      "requirements": ["pygithub"],
      "ignore": [
        "circle\\.yml$",
        "\\.git$",
        "/.*\\.pyc$"
      ],
      "timeout": 30,
      "memory": 512,
      "vpc": {
        "subnets": [
          "subnet-00000000"
        ],
        "security_groups": [
          "sg-00000000"
        ]
      }
    }

Command Line Usage
~~~~~~~~~~~~~~~~~~

To package and upload simply run the command from within your lambda
directory or with the directory as an option.

.. code:: shell

    lambda-uploader ./myfunc

To specify an alternative profile that has been defined in
``~/.aws/credentials`` use the ``--profile`` parameter.

.. code:: shell

    lambda-uploader --profile=alternative-profile

To specify an alternative, prexisting virtualenv use the
``--virtualenv`` parameter.

.. code:: shell

    lambda-uploader --virtualenv=~/.virtualenv/my_custom_virtualenv

To omit using a virtualenv use the ``--no-virtualenv`` parameter.

.. code:: shell

    lambda-uploader --no-virtualenv

To inject any other additional files, use the
``--extra-file EXTRA_FILE`` parameter.

.. code:: shell

    lambda-uploader --extra-file ~/stuff_for_lambda_packages

If you would prefer to upload another way you can tell the uploader to
ignore the upload. This will create a package and leave it in the
project directory.

.. code:: shell

    lambda-uploader --no-upload ./myfunc

To publish a version without an alias you would pass the the publish
flag.

.. code:: shell

    lambda-uploader -p ./myfunc

If you would like to alias your upload you can pass the alias with the
alias flag. The function description will be used when an
alias-description is not provided.

.. code:: shell

    lambda-uploader --alias myAlias --alias-description 'My alias description' ./myfunc

If you would prefer to build the package manually and just upload it
using uploader you can ignore the build. This will upload
``lambda_function.zip`` file.

.. code:: shell

    lambda-uploader --no-build
