#!/usr/bin/env python
#
# Harbinger runs on an internet-visible host and communicates with Github.
# Meant to be run on a schedule, it polls a collection of software projects
# for updates since the last logged version and posts an issue to the target
# project's github page indicating which dependency has a new version
# available.
# The polling logic to use for each project is defined by one or more plugin
# modules.

import os
import sys
import configparser
import urllib.request
import subprocess
from subprocess import run
import tarfile
import tempfile
import argparse
import shutil
from contextlib import contextmanager
import importlib

import yaml
import getpass
from abc import ABC, abstractmethod
import github3


@contextmanager
def pushd(newDir):
    '''Context manager function for shell-like pushd functionality

    Allows for constructs like:
    with pushd(directory):
        'code'...
    When 'code' is finished, the working directory is restored to what it
    was when pushd was invoked.'''
    previousDir = os.getcwd()
    os.chdir(newDir)
    yield
    os.chdir(previousDir)


class Plugin(ABC):
    def __init__(self, reference):
        super().__init__()
        #self.ref_ver_data = None
        #self.new_ver_data = None

    @abstractmethod
    def new_version_available(self):
        pass

    @abstractmethod
    def version_data(self):
        '''Return updated reference values that reflect what was obtained
        from the version query. All values returned here will become the
        updated reference dictionary.'''
        pass

    @abstractmethod
    def get_extra(self):
        '''Obtain any extra information the plugin has decided to provide
        for inclusion in the notification message. Things like changelog
        entries, API version specifics, etc, may be returned here.'''
        pass
    


class ReleaseNotifier():
    '''ReleaseNotifier class

    Parameters
    ----------
    depname: Dependency name (must map to a plugin name to support
                                    querying the version information.)
    params: Notification configuration for a single dependency.
                  (dict)
    refdir: The directory holding the reference version value for the
            dependency to be queried.
    '''
    github = None

    def __init__(self,
                 depname,
                 params,
                 refdir,
                 notify_repo,
                 gh_username=None,
                 gh_password=None):

        # Normalize path-like dependency names.
        self.dep_name = depname
        self.plugin_module = None
        self.params = params
        #self.github = None
        self.plugin = None
        self.plugin_extra = None  # Optional extra data to pass to a plugin.
        self.notify_repo = notify_repo
        self.gh_username = gh_username
        self.gh_password = gh_password
        self.refdir = os.path.abspath(refdir)
        self.refs_file = os.path.join(self.refdir, 'references.yml')
        self.refs = None
        self.md5 = None
        self.ref_md5 = None
        self.issue_title_base = 'Upstream release of dependency: '
        self.issue_title = self.issue_title_base + self.dep_name
        self.comment_base = ('This is a message from an automated system '
                'that monitors `{}` '
                'releases.\n'.format(self.dep_name))
        self.dry_run = False
        self.remote_ver = None
        self.read_refs()

    def load_plugin(self):
        if len(self.params.keys()) == 0:
            plugin_name = f'.plugins.relcheck_{depname}'
        else:
            plugin_name = '.plugins.' + self.params['plugin'].strip()
        print(f'plugin: {plugin_name}')
        try:
            self.plugin_module= importlib.import_module(plugin_name, 'harbinger')
        except ImportError as e:
            print(f'Import of plugin {plugin_name} failed.\n\n')
            raise(ImportError)
        # Change to temporary directory before creating plugin object
        # to provide a clean location for it to create files, if necessary.
        with tempfile.TemporaryDirectory() as tmpdir:
            with pushd(tmpdir):
                self.plugin = self.plugin_module.plugin(self.refs[self.dep_name])
                # TODO: Detect special extra steps needed by interrogating
                #       the plugin itself?
                if 'github' in plugin_name:
                    print('Authenticating with github API...')
                    self.github = github3.login(self.gh_username, self.gh_password)
                    self.plugin_extra = self.github

    def new_version_available(self):
        return self.plugin.new_version_available()

    def version_data(self):
        return self.plugin.version_data()

    def get_extra(self):
        return self.plugin.get_extra()

    def get_new_reference(self):
        return self.plugin.get_new_reference()

    def read_refs(self):
        with open(self.refs_file) as f:
            self.refs = yaml.safe_load(f)

    def reference_available(self):
        '''Is version reference data available for the dependency?

        Returns
        -------
        True if reference file is available.
        False otherwise.
        '''
        if self.dep_name in self.refs.keys():
            return True
        else:
            return False

    def post_github_issue(self):
        # Push changes text to a new/existing issue on Github.
        self.comment = self.comment_base + '/n' + self.comment
        if self.dry_run:
            print(self.comment)
        else:
            print('Posting comment to Github...')
            #if not self.github:
            if not ReleaseNotifier.github:
                print('authenticating')
                #self.github = github3.login(self.gh_username,
                #                            password=self.gh_password)
                ReleaseNotifier.github = github3.login(self.gh_username,
                                            password=self.gh_password)
            repo = self.notify_repo.split('/')
            print('posting now')
            ReleaseNotifier.github.create_issue(repo[0],
                    repo[1],
                    self.issue_title,
                    self.comment)

    def write_refs(self):
        with open(self.refs_file, 'w') as f:
            f.write(yaml.safe_dump(self.refs))

    def update_ref_data(self):
        '''Update version reference to inform the next run.'''
        self.refs[self.dep_name] = self.version_data()

    def check_for_release(self):
        self.load_plugin()
        if self.new_version_available():
            print(f'A version change has been detected for {self.dep_name}')
            if not self.reference_available():
                print('No existing version reference found for {}'.format(
                    self.dep_name))
                print('Storing remote version as new reference: {}'.format(
                    os.path.join(self.refdir, self.refs_file)))
            print(f'Reference: {self.refs[self.dep_name]}')
            self.comment = self.get_extra()
            self.update_ref_data()
            print(f'New      : {self.refs[self.dep_name]}')
            self.write_refs()
            # TODO: Implement version roll-back if issue posting fails.
            self.post_github_issue()
        else:
            print(f'No new version detected for {self.dep_name}')

