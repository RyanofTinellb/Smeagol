import os
import re
import tkinter.filedialog as fd

from .. import conversion, errors, utils, widgets, filesystem as fs
from ..defaults import default
from ..site import Site
from ..utilities import RandomWords


class Interface:
    def __init__(self, filename='', server=True):
        self.filename = filename
        config = self.load_config(filename) if filename else default.config
        self.setup(config)
        if server:
            self.port = fs.start_server(
                port=41809, directory=self.site.directory, page404=self.page404)

    def __getattr__(self, attr):
        if attr == 'site_info':
            return self.config.setdefault('site', {})
        elif attr == 'tabs':
            return self.config.setdefault('entries', [[]])
        else:
            try:
                return getattr(super(), attr)
            except AttributeError:
                name = self.__class__.__name__
                raise AttributeError(
                    f"'{name}' object has no attribute '{attr}'")

    def __setattr__(self, attr, value):
        if attr == 'markdown' and isinstance(value, conversion.Markdown):
            self.config['markdown'] = value.filename
        elif attr == 'styles' and isinstance(value, widgets.Styles):
            self.config['styles'] = dict(value.items())
        super().__setattr__(attr, value)

    @property
    def entries(self):
        k = [self.find_entry(e) for e in self.tabs]
        return k

    def load_config(self, filename):
        if filename.endswith('.smg'):
            config = fs.load(filename)
        else:
            config = default.config
            config['site']['files']['source'] = filename
        return config

    def setup(self, config):
        self.config = config
        self.site = Site(**config.get('site', None))
        self.translator = conversion.Translator()
        self.markdown = conversion.Markdown(config.get('markdown', None))
        self.styles = widgets.Styles(config.get('styles', None))
        self.linker = conversion.Linker(config.get('links', None))
        self.randomwords = RandomWords()

    def save(self):
        fs.save(self.config, self.filename)

    def find_entry(self, headings):
        entry = self.site.root
        if not headings:
            return entry
        for heading in headings:
            try:
                entry = entry[heading]
            except (KeyError, IndexError):
                break
        return entry

    def open_entry_in_browser(self, entry):
        fs.open_in_browser(self.port, entry.link)
        return 'break'

    def change_language(self, language):
        self.translator.select(language)
        self.randomwords.select(language)

    def save_page(self, text, entry):
        ''' text is formatted'''
        entry.text = self._save(text)
        for string, filename in self.site.publish(entry):
            if isinstance(string, Exception):
                raise string
            string = self.templates.html(entry)
            filename = os.path.join(self.site.directory, filename)
            fs.saves(string, filename)
        # Save source, wholepage

    def _save(self, text):
        text = self.markdown.to_markup(text)
        return text

    def _publish(self, text, entry):
        text = self.linker.add_links(text, entry)
        text = conversion.markup(text)
        return text

    def save_site(self):
        fs.save(**self.site.source_info)

    def close_servers(self):
        fs.close_servers()

    @property
    def page404(self):
        name = self.site.name
        page404 = default.page404.format(
            self.site[0].elder_links).replace(
            f'<li class="normal">{name}</li>',
            f'<li><a href="/index.html">{name}</a></li>'
        )
        page404 = re.sub(r'href="/*', 'href="/', page404)
