import os
import shutil
import ast
import yaml
import pytest
from harbinger.release_notifier import ReleaseNotifier
from harbinger.scanner import Scanner
from harbinger.mock_github3 import *

depname = 'test'
params = {'plugin': 'relcheck_test'}
notify_repo = 'testorg/testrepo'
refdir = os.path.abspath('tests')
reference = {'test': {'version': '0.0.0'}}
new_reference = {'test': {'version': '1.0.0'}}

# TODO: Conduct all tests in a sandbox.
# TODO: Write out the reference file into a known location for each test that
# requires it.

repos = ['testrepo']

def test_read_refs():
    scanner = Scanner('testorg', refdir,)
    assert scanner.refs == reference 

def test_write_refs(tmp_path):
    refs_file = os.path.join(tmp_path, 'references.yml')
    with open(refs_file, 'w') as f:
        for dep in reference:
            f.write(dep)
    scanner = Scanner('testorg', refdir)
    scanner.refs = new_reference
    scanner.refs_file = refs_file
    scanner.write_refs()
    assert scanner.refs == new_reference
    

# Fixtures
@pytest.fixture(scope='module')
def notifier():
    gh = mock_gh('tagname')
    n = ReleaseNotifier(depname,
                        params,
                        reference,
                        notify_repo,
                        gh)
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


#def test_post_github_issue():
#    pass


#def test_full_check():
#    noti = ReleaseNotifier(depname, params, refdir)
#    noti.check_for_release()


#def test_harbinger_cli():

