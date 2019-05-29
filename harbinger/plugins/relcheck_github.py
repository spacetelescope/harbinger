# Github-specific version update checker
# This is a special case of the general plugin structure as it requires
# an authenticated github3.py object to be available in order to perform
# the version queries via the Github API. Other plugins do not have this
# requirement and thus do not need the `github` argument on the __init__()
# call.
import copy
import github3

# TODO: Handle regex as a parameter to use when selecting tags?

class plugin():

    def __init__(self, params, ref_ver_data, github):

        self.ref_ver_data = ref_ver_data
        self.new_ver_data = copy.deepcopy(self.ref_ver_data)

        owner = params['name'].split('/')[0]
        repo = params['name'].split('/')[1]
        ghrepo = github.repository(owner, repo)
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
            #print("Checking for a Github-style release...")
            try:
                latestrel = ghrepo.latest_release()
            except Exception as e:  # TODO: can this be more specific?
                print('No Github release found for this repository.')
            self.tag_name = latestrel.tag_name
            # Github release found, examine the tag.
            #print('latestrel = {}'.format(latestrel))
            #print('tag_name  = {}'.format(self.tag_name))
            if self.tag_name[0] == 'v':
                self.version = self.tag_name[1:]
            else:
                self.version = self.tag_name
        if release_style == 'tag-only':
            print('Checking for a tag-style release...')
            print('Checking for tag of appropriate type to signify release...')
            self.version = 'tagoly'
        self.new_ver_data['version'] = self.version
    
    def new_version_available(self):
        return self.new_ver_data['version'] != self.ref_ver_data['version']

    def version_data(self):
        '''Return reference dict with updated version and other values.'''
        return(self.new_ver_data)

    def get_extra(self):
        return('No changelog')

