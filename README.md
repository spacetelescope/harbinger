# harbinger
Send a Github issue notifications to a repository containing information about a newly released version when select project dependencies are released upstream.

# Administrator Setup
This software is meant to be run as a periodically scheduled service (cron job) with appropriate Github credentials to allow it to post issues on the repositories in the organization or user account specified in the service's configuration.

## Installation
Clone this repository and then:
```
$ cd harbinger
$ python setup.py install
```

## Usage
```
$ harbinger --help

usage: harbinger [-h] [-p] [-u USERNAME] [-r REFDIR] [-o ORG]

Scan a Github organization or user account for repositories that contain a
harbinger.cfg file defining dependencies to monitor and post a notification
via Github issue if a release newer than the latest logged version is
available. Best run on a schedule to continuously monitor for dependency
updates.

optional arguments:
  -h, --help            show this help message and exit
  -p, --password        Prompt for interactive password entry. Overrides
                        default behavior of accepting the password to use via
                        the environment variable {password_envvar}.
  -u USERNAME, --username USERNAME
                        Prompt for interactive username entry. Overrides
                        default behavior of accepting the username to use via
                        the environment variable {username_envvar}.
  -r REFDIR, --refdir REFDIR
                        Directory where program will check for the reference
                        version file. When the flag is not used, the default
                        is the current working directory.
  -o ORG, --org ORG     Github organization (or user account) scan.

```

## Simple Server Setup

```
#   Set up a cron job to periodically execute
$ export HARBINGER_USER="<Github service account name>"
$ export HARBINGER_PW="<Github service account password>"
$ harbinger -r <persistent reference directory> -o <github organization>
```

# Configuration of Repositories
To allow `harbinger` to poll a given repository in an organization that has been configured as indicated above, simply add a text file to the root directory of the repository on the `master` branch named `harbinger.cfg`. Within this file, list the dependencies one wishes to monitor.


## Supported Dependency Types
The types of dependencies currently supported for monitoring:

* `cfitsio` - https://heasarc.gsfc.nasa.gov/fitsio/
* `Github repository`
  * Release style `github`:Projects released via full Github release objects may be polled.

### Config file
An example configuration file to be placed in the repository `example_org/example_repo1`

`harbinger.cfg`
```
[cfitsio]

[dependency_org/dependency1]
release_style: github
```

