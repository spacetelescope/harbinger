import os
import shutil
import pytest
from ..plugins import relcheck_github
from ..utils import pushd

params = {'name': 'org/reponame', 'release_style': 'github'}
test_reference = {'version': '1.0.0', 'soname': '1'}
test_dir = 'tests'
changelog = 'No changelog'


# Class hierarchy used to mock the components of github3.py
# used by the github plugin.
class mock_gh_release():
    def __init__(self, tag):
        self.tag_name = tag

class mock_gh_repository():
    def __init__(self, tag, release=True):
        self.tag = tag
        self.release = release
    def latest_release(self):
        if self.release:
            return(mock_gh_release(self.tag))

class mock_gh_repository_no_rel():
    def __init__(self, tag, release=True):
        self.tag = tag
        self.release = release

class mock_gh():
    def __init__(self, tag, release=True):
        self.tag = tag
        self.release = release
    def repository(self, owner, repo):
        if self.release:
            return(mock_gh_repository(self.tag, self.release))
        else:
            return(mock_gh_repository_no_rel(self.tag, self.release))

# Test functions

def test_new_version_no_release():
    with pytest.raises(Exception) as e_info:
        mock_norelease = mock_gh('tag', release=False)
        p = relcheck_github.plugin(params, test_reference, mock_norelease)


# Test definitions
mock_githubs = [
                mock_gh('1.0.0'),
                mock_gh('v1.0.0'),
                ]

@pytest.mark.parametrize('mock_github', mock_githubs)
def test_new_version_available(mock_github):
    p = relcheck_github.plugin(params, test_reference, mock_github)
    print(p.ref_ver_data)
    print(p.new_ver_data)
    p.new_ver_data['version'] = 'new_version'
    assert p.new_version_available()


@pytest.mark.parametrize('mock_github', mock_githubs)
def test_version_data(mock_github):
    p = relcheck_github.plugin(params, test_reference, mock_github)
    assert p.version_data() == test_reference


@pytest.mark.parametrize('mock_github', mock_githubs)
def test_get_extra(mock_github, tmpdir):
    p = relcheck_github.plugin(params, test_reference, mock_github)
    assert p.get_extra() == changelog


