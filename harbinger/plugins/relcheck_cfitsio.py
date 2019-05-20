# cfitsio-specific version update checker

import urllib.request
import tarfile
import copy

from ..release_notifier import Plugin

class plugin(Plugin):

    def __init__(self, ref_ver_data):
        '''Download and extract key files from source tarball.
        Read in header file.
        Read in changelog file.'''

        self.ref_ver_data = ref_ver_data
        self.new_ver_data = copy.deepcopy(self.ref_ver_data)

        latest_tar = 'cfitsio_latest.tar.gz'
        latest_URL = f'http://heasarc.gsfc.nasa.gov/FTP/software/fitsio/c/{latest_tar}'
        fitsio_h = 'cfitsio/fitsio.h'
        changesfile = 'cfitsio/docs/changes.txt'
    
        urllib.request.urlretrieve(latest_URL, latest_tar)
    
        tfile = tarfile.open(latest_tar, mode='r')
        tfile.extract(fitsio_h)
        tfile.extract(changesfile)
        with open(fitsio_h, 'r') as f:
            self.header = f.readlines()
        with open(changesfile) as f:
            self.changelog = f.readlines()
        # Extract version value from the source code. Update new_ver_data.
        for line in self.header:
            if 'CFITSIO_VERSION' in line.strip():
                self.version = line.strip().split()[2]
                #print(f'New version       {self.version}')
                self.new_ver_data['version'] = self.version
                break
        # Extract SONAME value from the source code. Update new_ver_data.
        self.soname = None
        for line in self.header:
            if 'CFITSIO_SONAME' in line.strip():
                self.soname = line.strip().split()[2]
                #print(f'New SONAME        {self.soname}')
                self.new_ver_data['soname'] = self.soname
                break

    def new_version_available(self):
        return self.new_ver_data['version'] != self.ref_ver_data['version']

    def version_data(self):
        '''Return reference dict with updated version and other values.'''
        return(self.new_ver_data)

    def get_extra(self):
        '''Return changelog and SONAME version comparison information for
        inclusion in the notification message.'''
        # TODO: Look into a regex solution to this?
        sec_open = False
        latest_changes = ''
        for line in self.changelog:
            if 'Version' in line.strip() and sec_open:
                break
            if 'Version' in line.strip() and not sec_open:
                sec_open = True
                latest_changes += line
                continue
            if sec_open:
                latest_changes += line
                continue
        ref_soname = self.ref_ver_data['soname']
        if ref_soname != self.soname:
            latest_changes += (
                    f'\n**NOTE: This release introduces a SONAME'
                    f'change from {ref_soname} to {self.soname}.**'
            )
        return(latest_changes)

