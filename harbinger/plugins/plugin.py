from abc import ABC, abstractmethod

class Plugin(ABC):
    def __init__(self, params, reference):
        super().__init__()
        #TODO: Investigate whether having these abstract properties
        #      streamlines things elsewhere.
        #self.ref_ver_data = None
        #self.new_ver_data = None

    @abstractmethod
    def new_version_available(self):
        '''Is a new version of the dependency available?'''

    @abstractmethod
    def version_data(self):
        '''Return updated reference values that reflect what was obtained
        from the version query. All values returned here will become the
        updated reference dictionary to use as the basis for future update
        checks.'''

    @abstractmethod
    def get_extra(self):
        '''Obtain any extra information the plugin has decided to provide
        for inclusion in the notification message. Things like changelog
        entries, API version specifics, etc, may be returned here.'''
