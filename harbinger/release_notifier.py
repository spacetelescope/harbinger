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


#@contextmanager
#def pushd(newDir):
#    '''Context manager function for shell-like pushd functionality
#
#    Allows for constructs like:
#    with pushd(directory):
#        'code'...
#    When 'code' is finished, the working directory is restored to what it
#    was when pushd was invoked.'''
#    previousDir = os.getcwd()
#    os.chdir(newDir)
#    yield
#    os.chdir(previousDir)


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
    gh_username: The Github username to use when authenticating for API
                 access. Default value: None
    gh_password: The Github password (or access token value) to use when
                 authenticating for API access. Default value: None

    '''
    github = None

    def __init__(self,
                 depname,
                 params,
                 refdir,
                 notify_repo,
                 gh_username=None,
                 gh_password=None):

        self.dep_name = depname
        self.plugin_module = None
        self.params = params
        self.plugin = None
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
        self.comment_base = (f'This is a message from an automated system '
                             f'that monitors `{self.dep_name}` releases.\n\n')
        self.dry_run = False
        self.remote_ver = None
        self.read_refs()

    def load_plugin(self):
        if '/' in self.dep_name:  # Github dependency
            plugin_name = f'.plugins.relcheck_github'
            if not ReleaseNotifier.github:
                print('Authenticating with github API...')
                ReleaseNotifier.github = github3.login(
                                                self.gh_username,
                                                password=self.gh_password)
        else:
            plugin_name = f'.plugins.relcheck_{self.dep_name}'
        print(f'plugin: {plugin_name}')
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
                    self.plugin = self.plugin_module.plugin(
                            self.params,
                            self.refs[self.dep_name],
                            ReleaseNotifier.github)
                else:
                    self.plugin = self.plugin_module.plugin(self.params,
                                                  self.refs[self.dep_name])

    def new_version_available(self):
        return self.plugin.new_version_available()

    def version_data(self):
        return self.plugin.version_data()

    def get_extra(self):
        return self.plugin.get_extra()

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
        # Push changes text to a new issue on Github.
        self.comment = self.comment_base + self.comment
        if self.dry_run:
            print(self.comment)
        else:
            print('Posting comment to Github...')
            if not ReleaseNotifier.github:
                print('Authenticating with github API...')
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
            # Update reference data
            self.refs[self.dep_name] = self.version_data()
            print(f'New      : {self.refs[self.dep_name]}')
            self.write_refs()
            # TODO: Implement version roll-back if issue posting fails.
            self.post_github_issue()
        else:
            print(f'No new version detected for {self.dep_name}')

