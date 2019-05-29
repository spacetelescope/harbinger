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
import importlib
import tempfile

import yaml
import github3
from .utils import pushd


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
    notify_repo: The Github repository that will receive an issue posting
                 should a dependency update be detected.
    gh: A github3.py object to use when interacting with Github.
        NOTE: Must be an authenticated connection if issues are to be posted
        successfully.
    '''
    github = None

# TODO: accept references, leave reading refs file to a higher layer.
    def __init__(self,
                 depname,
                 params,
                 ref,
                 notify_repo,
                 gh):

        self.dep_name = depname
        self.plugin_module = None
        self.params = params
        self.plugin = None
        self.notify_repo = notify_repo
        if not ReleaseNotifier.github:
            ReleaseNotifier.github = gh
        self.ref = ref
        self.issue_title_base = 'Upstream release of dependency: '
        self.issue_title = self.issue_title_base + self.dep_name
        self.comment_base = (f'This is a message from an automated system '
                             f'that monitors `{self.dep_name}` releases.\n\n')
        self.dry_run = False
        self.remote_ver = None

    def load_plugin(self):
        if '/' in self.dep_name:  # Github dependency
            plugin_name = f'.plugins.relcheck_github'
        else:
            plugin_name = f'.plugins.relcheck_{self.dep_name}'
        try:
            self.plugin_module = importlib.import_module(plugin_name, 'harbinger')
        except ImportError as e:
            print(f'Import of plugin {plugin_name} failed.\n\n')
            raise(ImportError)
        # Change to temporary directory before creating plugin object
        # to provide a clean location for it to create files, if necessary.
        with tempfile.TemporaryDirectory() as tmpdir:
            with pushd(tmpdir):
                # If depdency is hosted on Github, pass in the local github object
                # to use when making API queries, otherwise instantiate a normal
                # plugin object.
                if '/' in self.dep_name:  # Github dependency
                    self.params['name'] = self.dep_name
                    #print(f'self.ref = {self.ref}')
                    self.plugin = self.plugin_module.plugin(
                            self.params,
                            self.ref,
                            ReleaseNotifier.github)
                else:
                    self.plugin = self.plugin_module.plugin(self.params,
                                                  self.ref)

    def new_version_available(self):
        return self.plugin.new_version_available()

    def version_data(self):
        return self.plugin.version_data()

    def get_extra(self):
        return self.plugin.get_extra()

    def post_github_issue(self, reponame):
        # Push changes text to a new issue on Github.
        if self.dry_run:
            print(self.comment)
        else:
            repo = reponame.split('/')
            print(f'Posting {self.dep_name} version update notice to {repo[1]}...')
            ReleaseNotifier.github.create_issue(repo[0],
                    repo[1],
                    self.issue_title,
                    self.comment)

    def check_for_release(self):
        self.load_plugin()
        if self.new_version_available():
            print(f'A version change has been detected for {self.dep_name}')
            print(f'Reference: {self.ref}')
            self.comment = self.get_extra()
            # Update reference data
            self.ref = self.version_data()
            print(f'New      : {self.ref}')
            self.new_version_detected = True
            self.comment = self.comment_base + self.comment
            return True
        else:
            print(f'No new version detected for {self.dep_name}')
            self.new_version_detected = False
            return False

