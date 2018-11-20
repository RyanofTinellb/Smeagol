import sys
import os
import json
import re
from addremovelinks import AddRemoveLinks
from cwsmeagol.site.site import Site
from cwsmeagol.translation import *
from cwsmeagol.utils import *
from cwsmeagol.defaults import default
import tkFileDialog as fd
import tkSimpleDialog as sd

class Properties(object):
    def __init__(self, config=None, caller=None):
        super(Properties, self).__init__()
        self.caller = caller
        self.setup(config)

    def setup(self, config):
        self.config_filename = config
        try:
            with open(self.config_filename) as config:
                self.config = json.load(config)
        except (IOError, TypeError):
            self.config = json.loads(default.config)
        self.create_site()
        self.create_linkadder()
        self.translator = Translator(self.language)
        self.evolver = HighToVulgarLulani()
        self.randomwords = RandomWords(self.language)
        self.markdown = Markdown(self.markdown_file)

    def __getattr__(self, attr):
        if attr in {'files', 'source', 'destination', 'template',
                'template_file'}:
            return getattr(self.site, attr)
        elif attr in {'page', 'language', 'position', 'fontsize'}:
            return self.config['current'][attr]
        elif attr is 'markdown_file':
            return self.config['current']['markdown']
        else:
            return getattr(super(Properties, self), attr)

    def __setattr__(self, name, value):
        if name in {'page', 'language', 'position', 'fontsize'}:
            self.config['current'][name] = value
        elif name is 'markdown_file':
            self.config['current']['markdown'] = value
        elif name is 'markdown':
            try:
                super(Properties, self).__setattr__(name, Markdown(value))
            except TypeError: # value is already a Markdown instance
                super(Properties, self).__setattr__(name, value)
        else:
            super(Properties, self).__setattr__(name, value)

    def open_site(self):
        filetypes = [('Sm\xe9agol File', '*.smg'), ('Source Data File', '*.txt')]
        title = 'Open Site'
        filename = fd.askopenfilename(filetypes=filetypes, title=title)
        if filename and filename.endswith('.smg'):
            self.setup(filename)
            return False
        return filename

    def save_site(self, filename=None):
        self.page = list(self.heading_contents)
        self.config_filename = filename or self.config_filename
        if self.config_filename:
            with ignored(IOError):
                with open(self.config_filename, 'w') as config:
                    json.dump(self.config, config, indent=2)
                folder = os.getenv('LOCALAPPDATA')
                inifolder = os.path.join(folder, 'smeagol')
                inifile = os.path.join(inifolder, self.caller + '.ini')
                with ignored(os.error): # folder already exists
                    os.makedirs(inifolder)
                with open(inifile, 'a') as inisave:
                    pass    # ensure file exists
                try:
                    with open(inifile, 'r') as inisave:
                        sites = json.load(inisave)
                except ValueError:
                    sites = dict()
                with open(inifile, 'w') as inisave:
                    name = re.match(
                            r'.*/(.*?)\.',
                            self.config_filename
                        ).group(1).capitalize()
                    sites[name] = self.config_filename
                    json.dump(sites, inisave, indent=2)
                return # successful save
        self.save_site_as() # unsuccessful save

    def save_site_as(self):
        filetypes = [('Sm\xe9agol File', '*.smg')]
        title = 'Save Site'
        filename = fd.asksaveasfilename(filetypes=filetypes, title=title)
        if filename:
            filename = re.sub(r'(\.smg)?$', r'.smg', filename)
            self.config_filename = filename
            self.save_site()

    def update_site(self):
        """
        Update the current Site object with new properties from the
            config file.
        """
        for prop, value in self.config['site'].items():
            self.site.__dict__[prop] = value
        self.site.change_destination()

    def create_site(self):
        """
        Create a new Site object from the config info
        """
        self.site = Site(**self.config['site'])

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
