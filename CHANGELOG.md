lambda-uploader CHANGELOG
=========================

Unreleased
----------
- Added support for ignoring files
- Added the ability to use an existing virtual environment
- Fixed the temporary workspace name to prevent confusion
- Updated the virtualenv site-packages copy to include lib64 if it
  is not a symlink

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
