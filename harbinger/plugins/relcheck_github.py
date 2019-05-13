# Github-specific version update checker
# Two functions
#   get_version()
#   get_changelog()

import github3

def get_version(dep_id, params):
    '''Check for new release via method specified in 'params'.
    If the latest released version is later/greater than the value
    stored in the cache, return data about the release, otherwise
    return 'None'.'''

    #print('dep_id = {}'.format(dep_id)) 
    #print('params = {}'.format(params))
    version_info = None
    owner = dep_id.split('/')[0]
    repo = dep_id.split('/')[1]
    # TODO: To prevent API limits being breached, the (authenticated) github3
    # object from the calling script will need to make an appearance here.
    repo = github3.repository(owner, repo)
    # Determine the 'best' release version.
    # This will depend on how the repository is organized and how releases are done.
    # Easiest is if the repo uses Github releases consistently. Just query that.
    # Second best is a simple semver tag. Sort and pick the latest.
    # The problem is, these release practices have to be adhered to strictly, otherwise
    # incorrect information will be harvested here.
    #
    # What heuristic can be used to get only tags that look 'release-like'?
    release_style = params['release_style']

    if release_style == 'github':
        print("Checking for a Github-style release...")
        try:
            latestrel = repo.latest_release()
            tag_name = latestrel.tag_name
        except(github3.exceptions.NotFoundError):
            print('No Github release found for this repository.')
            return(version_info)
        # Github release found, examine the tag.
        print('latestrel = {}'.format(latestrel))
        print('tag_name  = {}'.format(tag_name))
        if tag_name[0] == 'v':
            version = tag_name[1:]
        else:
            version = tag_name
        version_info = {}
        version_info['version'] = version
        

    if release_style == 'tag-only':
        print('Checking for a tag-style release...')
        print('Checking for tag of appropriate type to signify release...')

        version_info = {}
        version_info['version'] = version

    return(version_info)
    

def get_changelog(ref_ver_data, new_ver_data):
    changelog = 'No changelog'
    return(changelog)
