import os
import shutil
import pytest
from ..plugins import relcheck_cfitsio
from ..utils import pushd

# TODO: Make this all self-contained by creating the tar.gz files
#       from data stored in this file and then running it through
#       the test routines.
params = {'plugin': 'relcheck_test'}
test_reference = {'version': '1.00', 'soname': '1'}
test_dir = 'tests'

tarball = 'cfitsio_test.tar.gz'
nonstd_tarball = 'cfitsio_test_nonstd.tar.gz'

changelog = ('Version x.01 - Mon Year\n'
'  - Changelog Entry 1\n'
'  - Changelog Entry 2\n'
'\n\n\n(For complete changelog information, consult the package changelog file in cfitsio/doc/changes.txt)')

parsefail_changelog = ('                   Log of Changes Made to CFITSIO\n'
'1\n x.01 - Mon Year\n3\n4\n x.00 - Mon Year\n6\n7\n8\n9\n10\n11\n12\n13\n14\n15'
'\n\n\n(For complete changelog information, consult the package changelog file '
'in cfitsio/doc/changes.txt)\n\n\n'
'  **NOTE: This release introduces a SONAME change from 0 to 1.**')

soname_notice = ('\n\n\n  **NOTE: This release introduces a SONAME '
        'change from 0 to 1.**')

changelog_w_soname = changelog + soname_notice


def test_new_version_available(tmpdir):
    shutil.copy(os.path.join(test_dir, tarball), tmpdir) 
    with pushd(tmpdir):
        p = relcheck_cfitsio.plugin(params, test_reference, tarball)
        assert (not p.new_version_available())

def test_version_data(tmpdir):
    shutil.copy(os.path.join(test_dir, tarball), tmpdir) 
    with pushd(tmpdir):
        p = relcheck_cfitsio.plugin(params, test_reference, tarball)
        assert p.version_data() == test_reference
        
def test_get_extra(tmpdir):
    shutil.copy(os.path.join(test_dir, tarball), tmpdir) 
    with pushd(tmpdir):
        p = relcheck_cfitsio.plugin(params, test_reference, tarball)
        assert p.get_extra() == changelog

def test_get_extra_w_soname(tmpdir):
    shutil.copy(os.path.join(test_dir, tarball), tmpdir) 
    with pushd(tmpdir):
        p = relcheck_cfitsio.plugin(params, test_reference, tarball)
        p.ref_ver_data['soname'] = '0'
        p.soname = '1'
        assert p.get_extra() == changelog_w_soname

def test_get_extra_nonstandard_changelog(tmpdir):
    shutil.copy(os.path.join(test_dir, nonstd_tarball), tmpdir) 
    with pushd(tmpdir):
        p = relcheck_cfitsio.plugin(params, test_reference, nonstd_tarball)
        assert p.get_extra() == parsefail_changelog
