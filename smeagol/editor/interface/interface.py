import os

from ...conversion import api as conversion
from ...site.site import Site
from ...utilities import api as utilities
from ...utilities import errors
from ...utilities import filesystem as fs
from ...utilities import utils
from ...widgets.styles.styles import Styles
from .assets import Assets
from .locations import Locations
from .templates import Templates


class Interface:
    def __init__(self, filename='', server=True, template_store=None):
        self.filename = filename
        config = self.load_config(filename) if filename else {}
        self.setup(config)
        self.site = self.open_site()
        self.template_store = template_store or {}
        if server:
            self.port = fs.start_server(
                port=41809, directory=self.locations.directory)

    def __getattr__(self, attr):
        match attr:
            case 'site_info':
                return self.config.setdefault('site', {})
            case '_entries':
                return self.config.setdefault('entries', [[]])
            case default:
                try:
                    return super().__getattr__(attr)
                except AttributeError:
                    raise errors.attribute_error(self, attr)

    def __setattr__(self, attr, value):
        match attr:
            case 'markdown':
                with utils.ignored(AttributeError):
                    self.config['markdown'] = value.filename
            case 'styles':
                with utils.ignored(AttributeError):
                    self.config['styles'] = dict(value.items())
        super().__setattr__(attr, value)

    def entries(self):
        return [self.find_entry(e) for e in self._entries]

    def load_config(self, filename):
        try:
            return self._load_config_file(filename)
        except AttributeError:
            return self._create_config(filename)

    @staticmethod
    def _load_config_file(filename):
        if filename.endswith('.smg'):
            return fs.load_yaml(filename)
        raise AttributeError('File type is Sméagol Source File. '
                             'Creating Sméagol Configuration File...')

    @staticmethod
    def _create_config(filename):
        return dict(assets=dict(source=filename))

    def save(self):  # alias for use by (e.g.) Editor
        self.save_config()

    def save_config(self):
        if self.filename:
            fs.save_yaml(self.config, self.filename)

    def setup(self, config):
        self.config = config
        self.assets = Assets(config.get('assets', {}))
        self.locations = Locations(config.get('locations', {}))
        self.templates = Templates(config.get('templates', {}))
        self.styles = self.open_styles(config.get('styles', ''))
        self.language = config.get('language', '')
        self.translator = conversion.Translator(self.language)
        self.markdown = conversion.Markdown(config.get('markdown', ''))
        self.linker = conversion.Linker(config.get('links', {}))
        samples = self.assets.samples
        self.randomwords = utilities.RandomWords(self.language, samples)

    def open_styles(self, styles):
        return Styles(fs.load_yaml(styles))

    def open_site(self):
        return Site(fs.load_yaml(self.assets.source))

    def save_site(self):
        fs.save_yaml(self.site.tree, self.assets.source)

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
    
    # def save_entry(self, entry, text):
    #     entry.text = text
    #     self.save_site()

    '''
    def save_page(self, text, entry):
        #  text is formatted
        self.update_entry(text, entry)

        entry.text = self._save(text)
        self.save_config()
        self.save_site()
        self.templates.set_data(entry, self.styles)
        html = self.templates.main.html
        filename = os.path.join(self.locations.directory, entry.link)
        fs.saves(html, filename)
        # Save wholepage'''
    
    def save_entry(self, entry):
        self.templates.set_data(entry, self.styles)
        html = self.templates.main.html()
        filename = os.path.join(self.locations.directory, entry.link)
        fs.save_string(html, filename)

    def close_servers(self):
        fs.close_servers()
