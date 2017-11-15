import sys
import os
import json
from .. import translation
from ..site.smeagol_site import Site
from smeagol_files import Files

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
        self.setup_template(template)
        self.setup_config(config)

    def setup_template(self, template):
        template = template or (
            os.path.join(os.path.dirname(__file__), 'editor_properties.json'))
        with open(template) as template:
            self.template = json.load(template)

    def setup_config(self, config):
        self.config_filename = config or (
            os.path.join(os.path.dirname(__file__), 'editor_properties.smg'))
        with open(self.config_filename) as config:
            self.config = json.load(config)

    @property
    def files(self):
        """
        Create a File object from the config info
        """
        return Files(**self.config['files'])

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

    def removelinkadder(self, kind):
        """
        Remove the linkadder of the appropriate type from configuration

        :param kind: (str) type of the adder
        """
        links = self.config['links']
        self.config['links'] = [adder for adder in links if adder['type'] != kind]

    def addlinkadder(self, kind, filename):
        self.removelinkadder(kind)
        if filename:
            self.config['links'].append(dict(type=kind, filename=filename))
        else:
            self.config['links'].append(dict(type=kind))

    def update(self, owner, prop, text, check, integer=False):
        """

        :raise: ValueError
        """
        if owner == 'links':
            if check:
                self.addlinkadder(prop, text)
            else:
                self.removelinkadder(prop)
        else:
            try:
                text = int(text) if integer else text
            except ValueError:
                text = 0
            self.config[owner][prop] = text

    def save(self, filename=None):
        self.config_filename = filename or self.config_filename
        with open(self.config_filename, 'w') as config:
            json.dump(self.config, config)