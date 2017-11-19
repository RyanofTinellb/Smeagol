import sys
import os
import json
from smeagol_files import Files
from addremovelinks import AddRemoveLinks
from cwsmeagol.site.smeagol_site import Site
from cwsmeagol.translation import *
import tkFileDialog as fd

class EditorProperties():
    """

    :param config: (str) name of a .smg Smeagol configuration file
    :param template: (str) name of a file containing all possible properties
    :param overwrite: (bool) save to source file? / lose current Site?

    properties:
        self.template
        self.config_filename - to save changes to
        self.config
        self.files - a Files object
        self.site - a Site object
        self.randomwords - a RandomWords object
        self.linkadder - a AddRemoveLinks object
    """
    def __init__(self, config=None, template=None, save=True):
        self.save = save
        self.setup_template(template)
        self.setup_config(config)
        self._site = self.create_site()

    """

    Open editor: make a new blank Site object.
    New Site: make a new blank Site object.
    Open an .smg file: make a new Site object with the .smg properties.
    Open a .txt file: make a new Site object from source.txt

    Save / Change Properties: do not make a new Site, modify the old one.

    """

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

    def open(self):
        """
        Loop until a valid file is passed back, or user cancels
        """
        filename = None
        while not filename:
            filetypes = [('Sm\xe9agol File', '*.smg')]
            title = 'Open Site'
            filename = fd.askopenfilename(filetypes=filetypes, title=title)
        self.setup_config(filename)

    def save(self, filename=None):
        self.config_filename = filename or self.config_filename
        with open(self.config_filename, 'w') as config:
            json.dump(self.config, config)

    def saveas(self):
        filetypes = [('Sm\xe9agol File', '*.smg')]
        title = 'Open Site'
        filename = fd.asksaveasfilename(filetypes=filetypes, title=title)
        if filename:
            self.save(filename)

    @property
    def files(self):
        """
        Create a File object from the config info
        """
        return Files(**self.config['files'])

    @property
    def site(self):
        return self._site


    def create_site(self):
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
        if self.config['random words']:
            return RandomWords(**self.config['random words'])
        else:
            return None

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

    def _removelinkadder(self, kind):
        """
        Remove the linkadder of the appropriate type from configuration

        :param kind: (str) type of the adder
        """
        links = self.config['links']
        self.config['links'] = [adder for adder in links if adder['type'] != kind]

    def _addlinkadder(self, kind, filename):
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
                self._addlinkadder(prop, text)
            else:
                self._removelinkadder(prop)
        else:
            try:
                text = int(text) if integer else text
            except ValueError:
                text = 0
            self.config[owner][prop] = text
