import os
import urllib
import configparser
import yaml
import github3
import json
from .release_notifier import *

class Scanner():

    def __init__(self,
                 org,
                 refdir,
                 username=None,
                 password=None,
                 dry_run=False):
        self.refs = None
        self.org = org
        self.refdir = os.path.abspath(refdir)
        self.refs_file = os.path.join(self.refdir, 'references.yml')
        self.read_refs()
        self.dep_requests = {}
        self.processed = []
        self.notifiers = {}
        self.cfg_file = 'harbinger.cfg'
        self.username = username
        self.password = password
        self.dry_run = dry_run
        print(f'username {username}')
        self.gh = github3.GitHub(username, password)
        self.acc = self.gh.user(org)

    def getjson(self, url):
        request = urllib.request.Request(url)
        result = urllib.request.urlopen(request)
        payload = result.read()
        jdata = json.loads(payload.decode())
        return jdata

    def get_repos(self):
        repos = []
        page = 1
        jdata = [1]
        while jdata != []:
            url = f'{self.acc.repos_url}?per_page=100&page={page}'
            jdata = self.getjson(url)
            for repo in jdata:
                repos.append(repo['name'])
            page += 1
        self.repos = repos
        return repos

    def read_refs(self):
        with open(self.refs_file) as f:
            self.refs = yaml.safe_load(f)

    def scan(self):
        print(f'Scanning {self.org}...')
        for repo in self.repos:
            # NOTE: This raw link takes a nonzero amount of time to reflect
            #       the file contents. Try using github3 instead to get a raw
            #       file blob.
            base_url = 'https://raw.githubusercontent.com/'
            url = f'{base_url}{self.org}/{repo}/master/{self.cfg_file}'
            request = urllib.request.Request(url)
            try:
                result = urllib.request.urlopen(request)
            except urllib.error.HTTPError as e:
                continue
            print(f'{repo}: Found config')
            rawconfig = str(result.read().decode())
            config = configparser.ConfigParser()
            config.read_string(rawconfig)
            sections = config.sections()
            repoconfig = {}
            for section in sections:
                repoconfig[section] = dict(config[section])
            self.dep_requests[repo] = repoconfig

    def check_for_releases(self):
        self.repos = self.get_repos()
        for repo in self.dep_requests:
            print(f'\nProcessing deps defined in {repo}')
            for dep in self.dep_requests[repo]:
                print(f'   {dep}')
                if dep not in self.notifiers:
                    ref = self.refs[dep]
                    noti = ReleaseNotifier(dep,
                                           self.dep_requests[repo][dep],
                                           ref,
                                           f'{self.org}/{repo}',
                                           self.gh,
                                           dry_run=self.dry_run)
                    noti.check_for_release()
                    self.notifiers[dep] = noti
                    if noti.new_version_detected:
                        self.refs[dep] = noti.ref
                if self.notifiers[dep].new_version_detected:
                    self.notifiers[dep].post_github_issue(f'{self.org}/{repo}')
                
    def write_refs(self):
        with open(self.refs_file, 'w') as f:
            f.write(yaml.safe_dump(self.refs))
