import os
from ...conversion import api as conversion
from ...widgets import api as widgets
from ...utilities import filesystem as fs
from ...utilities import utils
from ...site.site import Site
from ...utilities import api as utilities
from .template import templates
from .assets import Assets
from .locations import Locations

class Interface:
    def __init__(self, filename='', server=True):
        self.filename = filename
        config = self.load_config(filename) if filename else {}
        self.setup(config)
        self.site = self.open_site()
        if server:
            self.port = fs.start_server(
                port=41809, directory=self.locations.directory)

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
        if attr == 'markdown':
            with utils.ignored(AttributeError):
                self.config['markdown'] = value.filename
        elif attr == 'styles':
            with utils.ignored(AttributeError):
                self.config['styles'] = dict(value.items())
        super().__setattr__(attr, value)

    @property
    def entries(self):
        return [self.find_entry(e) for e in self.tabs]

    def load_config(self, filename):
        if filename.endswith('.smg'):
            return fs.load(filename)
        return dict(assets=dict(source=filename))

    def setup(self, config):
        self.config = config
        self.assets = Assets(config.get('assets', None))
        self.locations = Locations(config.get('locations', None))
        self.styles = widgets.Styles(config.get('styles', None))
        self.translator = conversion.Translator()
        self.markdown = conversion.Markdown(config.get('markdown', None))
        self.linker = conversion.Linker(config.get('links', None))
        self.randomwords = utilities.RandomWords()
        self.templates = templates.Templates(config.get('templates', None))
        
    def open_site(self):
        return Site(fs.load(self.assets.source))
    
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
        self.save_site()
        self.templates.set_data(entry=entry, styles=self.styles)
        html = self.templates.main_template.html
        filename = os.path.join(self.site.directory, entry.link)
        fs.saves(html, filename)
        # Save wholepage

    def _save(self, text):
        text = self.markdown.to_markup(text)
        text = self.styles.show_tags(text)
        return text

    def close_servers(self):
        fs.close_servers()