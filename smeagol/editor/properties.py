import sys
import os
import json
import re
from addremovelinks import AddRemoveLinks
from smeagol.site.site import Site
from smeagol.translation import *
from smeagol.utils import *
from smeagol.defaults import default
import tkFileDialog as fd
import tkSimpleDialog as sd


class Properties(object):
    def __init__(self, config=None, caller=None, master=None):
        self.setup(config)
        super(Properties, self).__init__(master)

    def setup(self, config):
        self.config_filename = config
        try:
            with open(self.config_filename) as config:
                self.configuration = json.load(config)
        except (IOError, TypeError):
            self.configuration = json.loads(default.config)
        self.site = Site(**self.site_info)
        self.linkadder = AddRemoveLinks(self.links)

    def setup_linguistics(self):
        # override Editor.setup_linguistics()
        self.translator = Translator(self.language)
        self.evolver = HighToColloquialLulani()
        self.randomwords = RandomWords(self.language)
        self.marker = Markdown(self.markdown_file)

    def __getattr__(self, attr):
        if attr in {'files', 'source', 'destination', 'template',
                'template_file', 'name', 'searchindex'}:
            return getattr(self.site, attr)
        elif attr in {'language', 'fontsize'}:
            return self.configuration['current'][attr]
        elif attr == 'markdown_file':
            return self.configuration['current']['markdown']
        elif attr in {'markdown', 'markup'}:
            return getattr(self.marker, 'to_{0}'.format(attr))
        elif attr in {'remove_links', 'add_links'}:
            return getattr(self.linkadder, attr)
        elif attr == 'links':
            return self.configuration['links']
        elif attr == 'site_info':
            return self.configuration['site']
        elif attr == 'history':
            return self.get_history()
        elif attr == 'page':
            return self.get_page()
        else:
            return getattr(super(Properties, self), attr)

    def __setattr__(self, attr, value):
        if attr in {'language', 'fontsize'}:
            self.configuration['current'][attr] = value
        elif attr == 'markdown_file':
            self.configuration['current']['markdown'] = value
        elif attr == 'marker':
            self.set_markdown(attr, value)
        elif attr in {'name', 'destination'}:
            self.configuration['site'][attr] = value
        elif attr in {'links', 'history'}:
            self.configuration[attr] = value
        elif attr == 'page':
            self.history.replace(value)
        else:
            super(Properties, self).__setattr__(attr, value)

    def set_markdown(self, attr, value):
        try:
            super(Properties, self).__setattr__(attr, Markdown(value))
        except TypeError: # value is already a Markdown instance
            super(Properties, self).__setattr__(attr, value)

    def get_history(self):
        history = self.configuration.get('history', [])
        if isinstance(history, ShortList):
            return history
        else:
            self.history = ShortList(history, 3)
            return self.history

    def get_page(self):
        try:
            return self.history[-1]
        except IndexError:
            return []

    def collate_config(self):
        self.name = self.site.name
        self.destination = self.site.destination
        self.links = self.linkadder.adders

    def open_site(self):
        filetypes = [('Sm\xe9agol File', '*.smg'), ('Source Data File', '*.txt')]
        title = 'Open Site'
        filename = fd.askopenfilename(filetypes=filetypes, title=title)
        if filename and filename.endswith('.smg'):
            self.setup(filename)
            return False
        return filename

    def save_site(self, filename=None):
        self.config_filename = filename or self.config_filename
        self.collate_config()
        if self.config_filename:
            with ignored(IOError):
                with open(self.config_filename, 'w') as config:
                    json.dump(self.configuration, config, indent=2)
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

    def update(self, properties):
        property = properties['property']
        owner = properties['owner']
        value = properties.get('value')
        checked = properties.get('checked')
        if owner == 'links':
            if checked:
                self.linkadder += {property: value}
            else:
                self.linkadder -= {property: value}
        else:
            setattr(self.site, property, value)
