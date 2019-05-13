import pytest
from harbinger.release_notifier import *

#@pytest.fixture(autouse=True)
depname = 'rendinam/auto-test'
params = {'plugin': 'relcheck_github', 'release_style': 'github'}
refdir = 'references'
#@pytest.fixture()
#def notifier():
#    notifier = ReleaseNotifier(depname, params, refdir)
#    #:yield notifier
#    return notifier


def test_gen_ref_filename():
    noti = ReleaseNotifier(depname, params, refdir)
    assert noti.gen_ref_filename() == 'references/rendinam-auto-test_reference'

#def test_query_remote(notifier):
#    print(notifier.depchecker)

def test_get_version():
    noti = ReleaseNotifier(depname, params, refdir)
    noti.query_remote()
    assert noti.get_version() == {'version': 'tag_2'}

def test_get_changelog():
    noti = ReleaseNotifier(depname, params, refdir)
    noti.query_remote()
    assert noti.get_changelog({'version': 'tag_2'}) == {'version': 'tag_3'}

def test_full_check():
    noti = ReleaseNotifier(depname, params, refdir)
    noti.check_for_release()

        
    
