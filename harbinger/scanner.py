# Iterate over all repos in a given org (or a single repo specified directly)
# For each repo that has a harbinger config file in the root dir of the
#   'master' branch, read the config and associate it with the repo name.
# For each dependency that has not yet been 

import github3
import urllib
import configparser
import yaml

from harbinger.release_notifier import *

user = True

orgs = ['spacetelescope']
# For orgs
#gh = github3.GitHub()
#reponames = []
#for org in orgs:
#    org = gh.organization(org)
#    repos = list(org.repositories())
#    for repo in repos:
#        reponames.append(repo.name)
#print(reponames)

dep_requests = {}
cfg_file = 'harbinger.cfg'
if user:
    user = 'rendinam'
    #repos = ['harbinger', 'test-1', 'test-2']
    repos = ['test-1', 'test-2']
    #repos = ['test-2']
    for repo in repos:
        url = f'https://raw.githubusercontent.com/{user}/{repo}/master/{cfg_file}'
        request = urllib.request.Request(url)
        result = urllib.request.urlopen(request)
        rawconfig = str(result.read().decode())
        config = configparser.ConfigParser()
        config.read_string(rawconfig)
        sections = config.sections()
        repoconfig = {}
        for section in sections:
            repoconfig[section] = dict(config[section])
        dep_requests[repo] = repoconfig

username_envvar = 'HARBINGER_USER'
password_envvar = 'HARBINGER_PW'
username = os.environ[username_envvar]
password = os.environ[password_envvar]

#for repo in dep_requests:
#    for dep in dep_requests[repo]:
#        print(repo, dep, dep_requests[repo][dep])
#        noti = ReleaseNotifier(dep,
#                               dep_requests[repo][dep],
#                               '../references',
#                               'rendinam/auto-test',
#                               username,
#                               password)
#        noti.check_for_release()


class Scanner():
    def __init__(self, refdir, repos):
        self.refs = None
        self.repos = repos
        self.refdir = os.path.abspath(refdir)
        self.refs_file = os.path.join(self.refdir, 'references.yml')
        self.read_refs()
        self.dep_requests = {}
        self.processed = []
        self.notifiers = {}
        self.scan()

    def read_refs(self):
        with open(self.refs_file) as f:
            self.refs = yaml.safe_load(f)

    def scan(self):
        for repo in self.repos:
            print(f'Scanning {repo}...')
            # NOTE: This raw link takes a nonzero amount of time to reflect
            #       the file contents. Try using github3 instead to get a raw
            #       file blob.
            url = f'https://raw.githubusercontent.com/{user}/{repo}/master/{cfg_file}'
            request = urllib.request.Request(url)
            result = urllib.request.urlopen(request)
            rawconfig = str(result.read().decode())
            config = configparser.ConfigParser()
            config.read_string(rawconfig)
            sections = config.sections()
            repoconfig = {}
            for section in sections:
                repoconfig[section] = dict(config[section])
            self.dep_requests[repo] = repoconfig

    def check_for_releases(self):
        for repo in self.dep_requests:
            print(f'    {repo}')
            for dep in self.dep_requests[repo]:
                    print(f'              {dep}')

        for repo in self.dep_requests:
            print(f'    {repo}')
            for dep in self.dep_requests[repo]:
                print(f'              {dep}')
                if dep not in self.notifiers:
                    ref = self.refs[dep]
                    noti = ReleaseNotifier(dep,
                                           dep_requests[repo][dep],
                                           ref,
                                           f'{user}/{repo}',
                                           username,
                                           password)
                    noti.check_for_release()
                    self.notifiers[dep] = noti
                    if noti.new_version_detected:
                        print('NEW VERSION')
                        self.refs[dep] = noti.ref
                if self.notifiers[dep].new_version_detected:
                    self.notifiers[dep].post_github_issue(f'{user}/{repo}')

                
    def write_refs(self):
        with open(self.refs_file, 'w') as f:
            f.write(yaml.safe_dump(self.refs))

##### main

scanner = Scanner('references', repos)
scanner.check_for_releases()
scanner.write_refs()
print('\nDependencies processed')
for dep in scanner.notifiers.keys():
    print(dep)



