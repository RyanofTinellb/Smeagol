import os

from smeagol.conversion import api as conversion
from smeagol.site.site import Site
from smeagol.utilities import api as utilities
from smeagol.utilities import filesystem as fs
from smeagol.utilities import utils
from smeagol.widgets.styles.styles import Styles
from smeagol.editor.interface import assets
from smeagol.editor.interface.templates.template_store import TemplateStore


class Interface:
    def __init__(self, filename='', server=True, template_store=None):
        self.filename = filename
        config = self.load_config(filename) if filename else {}
        self.setup(config)
        self.site = self.open_site()
        self.template_store = template_store or TemplateStore(self.templates)
        if server:
            self.port = fs.start_server(
                port=41809, directory=self.locations.directory)

    def __getattr__(self, attr):
        match attr:
            case 'site_info':
                return self.config.setdefault('site', {})
            case '_entries':
                return self.config.setdefault('entries', [[]])
            case _default:
                try:
                    return super().__getattr__(attr)
                except AttributeError as e:
                    name = type(self).__name__
                    raise AttributeError(
                        f"'{name}' object has no attribute '{attr}'") from e

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
        return {'assets': {'source': filename}}

    def save(self):  # alias for use by (e.g.) Editor
        self.save_config()

    def save_config(self):
        if self.filename:
            fs.save_yaml(self.config, self.filename)

    def setup(self, config):
        self.config = config
        self.assets = assets.Assets(config.get('assets', {}))
        self.locations = assets.Locations(config.get('locations', {}))
        self.templates = assets.Templates(config.get('templates', {}))
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
        fs.save_yaml(self.site.data, self.assets.source)

    def find_entry(self, headings):
        return self.site[headings]

    def open_entry_in_browser(self, entry):
        fs.open_in_browser(self.port, entry.link)
        return 'break'

    def change_language(self, language):
        self.translator.select(language)
        self.randomwords.select(language)

    def save_entry(self, entry):
        self.template_store.set_data(entry, self.styles)
        html = self.template_store.main.html
        filename = os.path.join(self.locations.directory, entry.link)
        print('lolly', html, filename)
        # fs.save_string(html, filename)

    def close_servers(self):
        fs.close_servers()
