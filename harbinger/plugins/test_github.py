import os
import shutil
import pytest
from ..plugins import relcheck_github
from ..utils import pushd
from ..mock_github3 import *

params = {'name': 'org/reponame', 'release_style': 'github'}
test_reference = {'version': '1.0.0', 'soname': '1'}
test_dir = 'tests'
changelog = 'No changelog'


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


