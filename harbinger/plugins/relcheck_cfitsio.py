# cfitsio-specific version update checker
# Two functions
# get_version()
# get_changelog()

import urllib.request
import tarfile

def get_version(dep_id, config, extra=None):
    verinfo = {}
    latest_tar = 'cfitsio_latest.tar.gz'
    latest_URL = 'http://heasarc.gsfc.nasa.gov/FTP/software/fitsio/c/{}'.format(latest_tar)
    reference_file = './cfitsio_reference'
    fitsio_h = 'cfitsio/fitsio.h'
    changesfile = 'cfitsio/docs/changes.txt'

    urllib.request.urlretrieve(latest_URL, latest_tar)

    tfile = tarfile.open(latest_tar, mode='r')
    tfile.extract(fitsio_h)
    tfile.extract(changesfile)
    ef = open(fitsio_h)
    lines = ef.readlines()

    # Extract version and SONAME values from the source code.
    for line in lines:
        if 'CFITSIO_VERSION' in line.strip():
            version = line.strip().split()[2]
            print('New version       {}'.format(version))
            break
    for line in lines:
        if 'CFITSIO_SONAME' in line.strip():
            soname = line.strip().split()[2]
            print('New SONAME        {}'.format(soname))
            break

    verinfo['version'] = version
    verinfo['soname'] = soname

    return(verinfo)
    

def get_changelog(ref_ver_data, new_ver_data, extra=None):
    ''' ******* Dependency-specific
    Accepts refvals object that gets returned from get_versions()'''
    fitsio_h = 'cfitsio/fitsio.h'
    latest_tar = 'cfitsio_latest.tar.gz'
    changesfile = 'cfitsio/docs/changes.txt'
    tfile = tarfile.open(latest_tar, mode='r')
    tfile.extract(changesfile)
    changelog = ''
    with open(changesfile) as cf:
        sec_open = False
        for line in cf.readlines():
            if 'Version' in line.strip() and sec_open:
                break
            if 'Version' in line.strip() and not sec_open:
                sec_open = True
                changelog += line
                continue
            if sec_open:
                changelog += line
                continue
    ef = open(fitsio_h)
    lines = ef.readlines()
    ref_soname = ref_ver_data['soname']
    soname = new_ver_data['soname']
    if ref_soname != soname:
        changelog += '\n**NOTE: This release introduces a SONAME change from {} to {}.**'.format(
            ref_soname, soname)
    return(changelog)
