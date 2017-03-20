import os

from os import path
from shutil import rmtree
from lambda_uploader import utils

TESTING_TEMP_DIR = '.testing_temp'

TEST_TREE = [
    'foo.py',
    'bar/foo.py',
    'bar/bar/foo.py',
    'ignore/foo.py',
    'ignore-me.py',
]
PATHS_TO_BE_IGNORED = [
    'ignore/foo.py',
    'ignore-me.py',
]

TEST_IGNORE = [
    'ignore/.*',
    'ignore-me.py',
    # The one below would exclude all the files if files to be ignored were
    # matched based on the full path, rather than the path relative to the
    # source directory, since the source directory contains 'test' in its path.
    'tests',
]

IGNORE_TEMP = [
    r'^\.[^.].*',
    r'.*\.pyc$'
]


def test_copy_tree():
    os.mkdir(TESTING_TEMP_DIR)
    for fil in TEST_TREE:
        dir = path.dirname(fil)
        test_pth = path.join(TESTING_TEMP_DIR, dir)
        if dir is not None and not path.isdir(test_pth):
            os.makedirs(test_pth)
        with open(path.join(TESTING_TEMP_DIR, fil), 'w') as tfile:
            tfile.write(fil)

    copy_dir = '.copy_of_test'
    utils.copy_tree(TESTING_TEMP_DIR, copy_dir, TEST_IGNORE)
    for fil in TEST_TREE:
        pth = path.join(copy_dir, fil)
        assert path.isfile(pth) is (fil not in PATHS_TO_BE_IGNORED)

    rmtree(TESTING_TEMP_DIR)
    rmtree(copy_dir)

def test_copy_tree_with_symlink():
    os.mkdir(TESTING_TEMP_DIR)
    filename = 'foo.py'
    symlink_filename = "sym-{}".format(filename)
    with open(path.join(TESTING_TEMP_DIR, filename), 'w') as tfile:
        tfile.write(filename)
    os.symlink(path.join(TESTING_TEMP_DIR,filename), path.join(TESTING_TEMP_DIR,symlink_filename))
    copy_dir = '.copy_of_test'

    utils.copy_tree(TESTING_TEMP_DIR, copy_dir)

    assert os.path.islink(path.join(copy_dir,symlink_filename))
    linkto = os.readlink(path.join(copy_dir,symlink_filename))
    assert linkto == path.join(copy_dir, filename)

    rmtree(TESTING_TEMP_DIR)
    rmtree(copy_dir)



def test_ignore_file():
    ignored = utils._ignore_file('ignore/foo.py', TEST_IGNORE)
    assert ignored

    ignored = utils._ignore_file('ignore', TEST_IGNORE)
    assert not ignored

    ignored = utils._ignore_file('bar/foo.py', TEST_IGNORE)
    assert not ignored


def test_ignore_file_dotfile():
    ignored = utils._ignore_file('.mydotfile', IGNORE_TEMP)
    assert ignored


def test_ignore_pyc():
    ignored = utils._ignore_file('pycharm', IGNORE_TEMP)
    assert not ignored

    ignored = utils._ignore_file('bar/foo.pyc', IGNORE_TEMP)
    assert ignored

