import os
import sys

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
    assert path.isdir(temp_workspace) == False


def test_prepare_workspace():
    temp_workspace = path.join(TESTING_TEMP_DIR,
                               package.TEMP_WORKSPACE_NAME)

    pkg = package.Package(TESTING_TEMP_DIR)
    pkg.prepare_workspace()
    pkg.prepare_virtualenv()
    assert path.isdir(temp_workspace)
    assert path.isdir(path.join(temp_workspace, 'venv'))
    if sys.platform == 'win32' or sys.platform == 'cygwin':
        assert path.isfile(path.join(temp_workspace, "venv\\Scripts\\pip.exe"))
    else:
        assert path.isfile(path.join(temp_workspace, 'venv/bin/pip'))


def test_install_requirements():
    reqs = ['pytest']
    temp_workspace = path.join(TESTING_TEMP_DIR,
                               package.TEMP_WORKSPACE_NAME)

    pkg = package.Package(TESTING_TEMP_DIR)
    # pkg.prepare_workspace()
    pkg.install_requirements(reqs)
    site_packages = path.join(temp_workspace,
                              'venv/lib/python2.7/site-packages')
    if sys.platform == 'win32' or sys.platform == 'cygwin':
        site_packages = path.join(temp_workspace, "venv\\lib\\site-packages")

    assert path.isdir(path.join(site_packages, '_pytest'))


def test_existing_virtualenv():
    pkg = package.Package(TESTING_TEMP_DIR, 'abc')
    assert pkg._pkg_venv == 'abc'


def test_package():
    pkg = package.Package(TESTING_TEMP_DIR)
    pkg.package()
    assert path.isfile(path.join(TESTING_TEMP_DIR, 'lambda_function.zip'))
