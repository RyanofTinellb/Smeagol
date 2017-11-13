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

    properties:
        self.template
        self.config_filename - to save changes to
        self.config
        self.files - a Files object
        self.site - a Site object
        self.randomwords - a RandomWords object
        self.linkadder - a AddRemoveLinks object
    """
    def __init__(self, config=None, template=None):
        self.setup_config(config)
        self.setup_template(template)

    def setup_template(self, template):
        template = template or os.path.dirname(sys.argv[0]) + '\\editor_properties.json'
        with open(template) as template:
            self.template = json.load(template)

    def setup_config(self, config):
        self.config_filename = config
        try:
            with open(config) as config:
                self.config = json.load(config)
        except TypeError:
            self.config = dict()

    @property
    def files(self):
        """
        Create a File object from the config info
        """
        return Files(**self.config['file'])

    @property
    def site(self):
        """
        Create a Site object from the config info
        """
        dict_ = self.config['site']
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

    def save(self, filename=None):
        self.config_filename = filename or self.config_filename
        with open(self.config_filename, 'w') as config:
            json.dump(self.config, config)
