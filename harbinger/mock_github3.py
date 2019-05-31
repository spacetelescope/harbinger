
# Class hierarchy used to mock the components of github3.py for testing.
class mock_gh_release():
    def __init__(self, tag):
        self.tag_name = tag

class mock_gh_repository():
    def __init__(self, tag, release=True):
        self.tag = tag
        self.release = release
    def latest_release(self):
        if self.release:
            return(mock_gh_release(self.tag))

class mock_gh_repository_no_rel():
    def __init__(self, tag, release=True):
        self.tag = tag
        self.release = release

class mock_gh():
    def __init__(self, tag, release=True):
        self.tag = tag
        self.release = release
    def repository(self, owner, repo):
        if self.release:
            return(mock_gh_repository(self.tag, self.release))
        else:
            return(mock_gh_repository_no_rel(self.tag, self.release))
