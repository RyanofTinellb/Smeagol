import sys
import os
import json
import re
from smeagol_files import Files
from addremovelinks import AddRemoveLinks
from cwsmeagol.site.smeagol_site import Site
from cwsmeagol.translation import *
import tkFileDialog as fd
import tkSimpleDialog as sd

class EditorProperties():
    """

    :param config: (str) name of a .smg Smeagol configuration file
    :param template: (str) name of a file containing all possible properties

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
        self.config_filename = config
        self.setup_config()
        self.create_site()
        self.create_random_words()
        self.create_linkadder()

    def setup_template(self, template):
        template = template or os.path.join(os.path.dirname(__file__),
                                                'editor_properties.json')
        with open(template) as template:
            self.template = json.load(template)

    def setup_config(self, config=None):
        config_filename = config or self.config_filename or (
            os.path.join(os.path.dirname(__file__), 'editor_properties.smg'))
        with open(config_filename) as config:
            self.config = json.load(config)

    @property
    def files(self):
        return self.site.files

    @property
    def source(self):
        return self.site.source

    def open(self):
        filetypes = [('Sm\xe9agol File', '*.smg'), ('Source Data File', '*.txt')]
        title = 'Open Site'
        filename = fd.askopenfilename(filetypes=filetypes, title=title)
        if filename and filename.endswith('.smg'):
            self.config_filename = filename
            self.setup_config()
            self.create_site()
            self.create_random_words()
            self.create_linkadder()
            return False
        return filename

    def save(self, filename=None):
        self.config_filename = filename or self.config_filename
        if self.config_filename:
            with open(self.config_filename, 'w') as config:
                json.dump(self.config, config, indent=2)
        else:
            self.saveas()

    def saveas(self):
        filetypes = [('Sm\xe9agol File', '*.smg')]
        title = 'Save Site'
        filename = re.sub(r'(\.smg)?$', r'.smg', fd.asksaveasfilename(filetypes=filetypes, title=title))
        if filename:
            self.config_filename = filename
            self.save()

    def collate_files(self):
        """
        Create a File object from the config info
        """
        return Files(**self.config['files'])

    def update_site(self):
        """
        Update the current Site object with new properties from the
            config file.
        """
        for prop, value in self.config['site'].items():
            self.site.__dict__[prop] = value
        self.site.files = self.collate_files()
        self.site.change_destination()

    def create_site(self):
        """
        Create a new Site object from the config info
        """
        dict_ = dict(self.config['site'])
        dict_['files'] = self.collate_files()
        self.site = Site(**dict_)

    def create_random_words(self):
        """
        Create a RandomWords object from the config info
        """
        if 'random words' in self.config:
            self.randomwords = RandomWords(**self.config['random words'])
        else:
            self.randomwords = None

    def create_linkadder(self):
        """
        Create an AddRemoveLinks instance from the config info
        """
        self.linkadder = AddRemoveLinks(map(self._links, self.config['links']))

    def _links(self, linkadder):
        import addremovelinks as translation
        try:
            linkadder = getattr(translation, linkadder['type'])()
        except TypeError:
            linkadder, resource = linkadder['type'], linkadder['resource']
            linkadder = getattr(translation, linkadder)(resource)
        return linkadder

    def _removelinkadder(self, kind):
        """
        Remove the linkadder of the appropriate type from configuration

        :param kind: (str) type of the adder
        """
        links = self.config['links']
        self.config['links'] = [adder for adder in links if adder['type'] != kind]

    def _addlinkadder(self, kind, resource):
        self._removelinkadder(kind)
        if resource:
            self.config['links'].append(dict(type=kind, resource=resource))
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
