import os
import argparse
import getpass
import configparser

from ..release_notifier import *


def main():
    
    username_envvar = 'HARBINGER_USER'
    password_envvar = 'HARBINGER_PW'
    
    parser = argparse.ArgumentParser(prog='harbinger')
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
    parser.add_argument('-c',
                        '--config',
                        type=str,
                        help='Required. Configuration file defining dependencies '
                        'to query.')
    parser.add_argument('notify_repo',
                        type=str,
                        help='Required. Repository in which an issue comment '
                        'should be posted. Specified in the form '
                        '<organization>/<repository>')
    
    args = parser.parse_args()
    
    if not args.config:
        print('Provide a config file name as an argument by using "-c/--config".')
        sys.exit(1)
    
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
    
    # Read config file.
    config = configparser.ConfigParser()
    config.read(args.config)
    depnames = config.sections()

    # For each dependency defined in the config, query it for new releases
    # and post a notification if one is found.
    for depname in depnames:
        print(f'Querying remote dependency {depname}')
        params = dict(config[depname])
        n = ReleaseNotifier(depname, params, refdir, username, password)
        try:
            n.check_for_release()
        except Exception as e:
            print(f'Failure in check_for_release() of {depname}.')
        print()
