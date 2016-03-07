import os
import sys
import pytest

from shutil import rmtree
from os import path
from lambda_uploader import package

TESTING_TEMP_DIR = '.testing_temp'


def setup_module(module):
    print('calling setup')
    os.mkdir(TESTING_TEMP_DIR)


def teardown_module(module):
    print('calling teardown')
    rmtree(TESTING_TEMP_DIR)


def test_package_zip_location():
    pkg = package.Package(TESTING_TEMP_DIR)
    assert pkg.zip_file == '.testing_temp/lambda_function.zip'


def test_package_clean_workspace():
    temp_workspace = path.join(TESTING_TEMP_DIR,
                               package.TEMP_WORKSPACE_NAME)
    os.mkdir(temp_workspace)

    pkg = package.Package(TESTING_TEMP_DIR)
    pkg.clean_workspace()
    assert path.isdir(temp_workspace) is False


def test_prepare_workspace():
    temp_workspace = path.join(TESTING_TEMP_DIR,
                               package.TEMP_WORKSPACE_NAME)

    pkg = package.Package(TESTING_TEMP_DIR)
    pkg.requirements(['pytest'])
    pkg.install_dependencies()
    assert path.isdir(temp_workspace)
    assert path.isdir(path.join(temp_workspace, 'venv'))
    if sys.platform == 'win32' or sys.platform == 'cygwin':
        assert path.isfile(path.join(temp_workspace, "venv\\Scripts\\pip.exe"))
    else:
        assert path.isfile(path.join(temp_workspace, 'venv/bin/pip'))


def test_install_requirements():
    temp_workspace = path.join(TESTING_TEMP_DIR,
                               package.TEMP_WORKSPACE_NAME)

    pkg = package.Package(TESTING_TEMP_DIR)
    pkg.requirements(['pytest'])
    pkg.install_dependencies()

    site_packages = path.join(temp_workspace,
                              'venv/lib/python2.7/site-packages')
    if sys.platform == 'win32' or sys.platform == 'cygwin':
        site_packages = path.join(temp_workspace, "venv\\lib\\site-packages")

    assert path.isdir(path.join(site_packages, '_pytest'))


def test_default_virtualenv():
    temp_workspace = path.join(TESTING_TEMP_DIR,
                               package.TEMP_WORKSPACE_NAME)
    reqs = ['pytest']
    pkg = package.Package(TESTING_TEMP_DIR)
    pkg.requirements = reqs
    pkg._build_new_virtualenv()
    # ensure we picked a real venv path if using default behavior
    assert pkg._pkg_venv == ("%s/venv" % temp_workspace)


def test_existing_virtualenv():
    venv_dir = "virtualenv_test"
    temp_virtualenv = path.join(TESTING_TEMP_DIR, venv_dir)
    os.mkdir(temp_virtualenv)

    pkg = package.Package(TESTING_TEMP_DIR, temp_virtualenv)
    pkg.virtualenv(temp_virtualenv)
    pkg.install_dependencies()

    assert pkg._pkg_venv == temp_virtualenv


def test_bad_existing_virtualenv():
    pkg = package.Package(TESTING_TEMP_DIR)
    with pytest.raises(Exception):
        pkg.virtualenv('abc')


def test_omit_virtualenv():
    pkg = package.Package(TESTING_TEMP_DIR)
    pkg.virtualenv(False)
    pkg.install_dependencies()
    assert pkg._pkg_venv is False


def test_package():
    pkg = package.Package(TESTING_TEMP_DIR)
    pkg.package()
    assert path.isfile(path.join(TESTING_TEMP_DIR, 'lambda_function.zip'))


def test_package_name():
    pkg = package.Package(TESTING_TEMP_DIR, zipfile_name='test.zip')
    pkg.package()
    assert path.isfile(path.join(TESTING_TEMP_DIR, 'test.zip'))
