lambda-uploader CHANGELOG
=========================

1.3.1
-----
- Fix race condition during upload and publish

1.3.0
-----
- Add support for Python3 Virtual Environments
- Fix copy source path
- Allow specification of runtime in configuration file

1.2.0
-----
- Added support for X-Ray tracing
- Added support for configuring a Kinesis subscription
- Symlinks can now be copied when creating the Lambda Package
- VPC Configuration is fixed
- Boto3, Botocore and Lambda Uploader Versions are now reported as part
  of traceback.

1.1.0
-----
- Runtime is now a configurable option
- Exclusion regexes now quoted properly
- Added support for Lambda environment variables
- Boto3 version dependency updated to support Step functions

1.0.3
-----
- Fixed issue in copy trees attempting to make a parent directory even
  if it already exists.
- Fixed issue in configuration verify where the object was not actually
  checked.

1.0.2
-----
- Bumped the boto3 version to 1.4.0

1.0.1
-----
- Fixed exceptions caused by not handling find_executable() returning
  None
- No longer raising exception in shell if Python version is Python 3
- Fixed issue with default requirements file not being used if it
  exists in the project directory
- Ignore list now applies to extra files as well

1.0.0
-----
- Warn if the lambda package is over the current AWS max size of 50MB
- Add --extra-file flag for adding arbitrary file(s) outside of the
  project directory.
- Add --requirements flag to allow setting a requirements file as a CLI
  option
- Updated the Package() object so only the build() method actually needs
  to be called.
- Updated the Package() constructor and removed most of the allowed
  variables in favor of calling setter methods.
- Add -c shorthand to the --config flag
- Fixed the ignores to match against paths relative to the source dir
- Added support for placing your lambda functions in specific VPC 
  subnets and security groups

0.5.1
-----
- Set hard Python requirements on 2.7
- Fixed issue with lambda-uploader only looking for requirements.txt in the cwd

0.5.0
-----
- Added optional zip file name to package class(API only)
- Updated boto3 version to 1.2.2

0.4.0
-----
- Added support for ignoring files
- Added the ability to use an existing virtual environment
- Fixed the temporary workspace name to prevent confusion
- Updated the virtualenv site-packages copy to include lib64 if it
  is not a symlink
- Add --no-virtualenv flag and set the default behavior to no longer create
  a virtual environment unless package requirements are found

0.3.0
-----
- Added flag to allow specifying the lambda.json path
- Added a role flag and environment variable to use in lieu of setting
  it in the config

0.2.2
-----
- Fixed issue with multiple requirements set in the config causing
  an error

0.2.1
-----
- Bumped version to deal with pypi failing

0.2.0
-----
- Added support for updating the lambda configuration
- Added a publish flag to the cli
- Added support for AWS profiles
- Added support for creating versions with aliases

0.1.1
-----
- Fixed a bug causing the source copy to not create parent directories

0.1.0
-----
- Intial release
