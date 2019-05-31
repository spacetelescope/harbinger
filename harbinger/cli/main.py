# Iterate over all repos in a given org (or a single repo specified directly)
# For each repo that has a harbinger config file in the root dir of the
#   'master' branch, read the config and associate it with the repo name.
# For each dependency that has not yet been 
import os
import sys
import argparse
import github3
import urllib
import configparser
import yaml
import json

from harbinger.release_notifier import *
from harbinger.scanner import *

def main():

    username_envvar = 'HARBINGER_USER'
    password_envvar = 'HARBINGER_PW'

    descrip = (f'Scan a Github organization or user account for repositories that'
    f' contain a harbinger.cfg file defining dependencies to monitor and '
    f'post a notification via Github issue if a release newer than the latest'
    f' logged version is available. Best run on a schedule to continuously '
    f'monitor for dependency updates.\n')
    parser = argparse.ArgumentParser(prog='harbinger', description=descrip)
    parser.add_argument('-p',
                        '--password',
                        action='store_true',
                        help=f'Prompt for interactive password entry. Overrides'
                        ' default behavior of accepting the password to use via '
                        ' the environment variable {password_envvar}.')
    parser.add_argument('-d',
                        '--dry-run',
                        action='store_true',
                        help='All output to local console. Does not communicate '
                        ' with Github.')
    parser.add_argument('-u',
                        '--username',
                        type=str,
                        help=f'Prompt for interactive username entry. Overrides'
                        ' default behavior of accepting the username to use via '
                        ' the environment variable {username_envvar}.')
    parser.add_argument('-r',
                        '--refdir',
                        type=str,
                        help='Directory where program will check for the reference'
                        ' version file. When the flag is not used, the default is '
                        'the current working directory.')
    parser.add_argument('-o',
                        '--org',
                        type=str,
                        help='Github organization (or user account) scan.')
   
    args = parser.parse_args()

    if not args.dry_run:
        if not args.username:
            try:
                username = os.environ[username_envvar]
            except KeyError:
                print('Environment variable {} not defined.')
                print('Store the Github password in that variable or run with '
                      '`-p` to prompt for the password interactively.'.format(
                          username_envvar))
                sys.exit(1)
        else:
            username = args.username
    
        if args.password:
            password = getpass.getpass()
        else:
            try:
                password = os.environ[password_envvar]
            except KeyError:
                print('Environment variable {} not defined.')
                print('Store the Github password in that variable or run with '
                      '`-p` to prompt for the password interactively.'.format(
                          password_envvar))
                sys.exit(1)
    
    if not args.refdir:
        refdir = './'
    else:
        refdir = args.refdir

    org = args.org
    
    username = os.environ[username_envvar]
    password = os.environ[password_envvar]
    
    scanner = Scanner(org, 'references', username, password)
    repos = scanner.get_repos()
    scanner.scan()
    scanner.check_for_releases()
    scanner.write_refs()
