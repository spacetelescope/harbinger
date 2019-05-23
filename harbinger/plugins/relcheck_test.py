# Plugin to use for testing.

from ..plugins import plugin

class plugin(plugin.Plugin):

    def __init__(self, params, ref_ver_data):
        pass

    def new_version_available(self):
        return(True)

    def version_data(self):
        return({'version': '0.0.0'})

    def get_extra(self):
        return('Extra info')
