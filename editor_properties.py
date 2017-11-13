import sys
import os
import json
import translation
from smeagol_site import Site
from smeagol_files import Files
from translation import AddRemoveLinks, RandomWords

class EditorProperties():
    """

    :param config_filename: (str) name of a .smg Smeagol configuration file
    """
    def __init__(self, config_filename=None):
        os.chdir(os.path.dirname(sys.argv[0]))
        with open('editor_properties.json') as template:
            self.template = json.load(template)
        try:
            with open(config_filename) as config:
                self.config = json.load(config)
        except TypeError:
            self.config = dict()

    def get_dict(self, kind):
        """
        Get names of keys from editor properties

        :param kind: (str) name of the property owner
        """
        keys = [key['property'] for key in self.template if key['owner'] == kind]
        return {key: self.config.get(key) for key in keys}

    @property
    def files(self):
        """
        Create a File object from the config info
        """
        return Files(**self.get_dict('file'))

    @property
    def site(self):
        """
        Create a Site object from the config info
        """
        dict_ = self.get_dict('site')
        dict_['files'] = self.files
        return Site(**dict_)

    @property
    def randomwords(self):
        """
        Create a RandomWords object from the config info
        """
        return RandomWords(**self.config['random words'])

    @property
    def linkadder(self):
        """
        Create an AddRemoveLinks instance from the config info
        """
        return AddRemoveLinks(map(self._links, self.config['links']))

    def _links(self, linkadder):
        try:
            linkadder = getattr(translation, linkadder)()
        except TypeError:
            linkadder, filename = linkadder['type'], linkadder['filename']
            linkadder = getattr(translation, linkadder)(filename)
        return linkadder
