import os
import shutil
import ast
import yaml
import pytest
from harbinger.release_notifier import *

depname = 'test'
params = {'plugin': 'relcheck_test'}
refdir = os.path.abspath('tests')
notify_repo = 'testorg/testrepo'
test_reference = {'version': '0.0.0'}

# TODO: Conduct all tests in a sandbox.
# TODO: Write out the reference file into a known location for each test that
# requires it.

# Fixtures
@pytest.fixture(scope='module')
def notifier():
    n = ReleaseNotifier(depname,
                        params,
                        refdir,
                        notify_repo)
    return(n)

#-----

def test_load_plugin(notifier):
    notifier.load_plugin()


def test_new_version_available(notifier):
    notifier.load_plugin()
    assert notifier.new_version_available() == True


def test_version_data(notifier):
    notifier.load_plugin()
    assert notifier.version_data() == {'version': '0.0.0'}


def test_get_extra(notifier):
    notifier.load_plugin()
    assert notifier.get_extra() == 'Extra info'


def test_reference_available(notifier):
    assert notifier.reference_available() == True


def test_reference_not_available(notifier):
    notifier.dep_name = None
    assert notifier.reference_available() == False

#def test_post_github_issue():
#    pass


def test_read_refs(notifier):
    notifier.read_refs()
    assert notifier.refs == {'test': {'version': '0.0.0'}}


def test_write_refs(notifier, tmp_path):
    notifier.refs_file = os.path.join(tmp_path, 'reference.yml.test')
    notifier.write_refs()
    # Read in and compare
    with open(notifier.refs_file, 'r') as f:
        new_refs = yaml.safe_load(f.read())
    assert new_refs[depname]['version'] == notifier.refs[depname]['version']


#def test_full_check():
#    noti = ReleaseNotifier(depname, params, refdir)
#    noti.check_for_release()


#def test_harbinger_cli():

