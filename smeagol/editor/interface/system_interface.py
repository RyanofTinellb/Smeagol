import os

from smeagol.editor.interface import assets
from smeagol.editor.interface.templates.template_store import TemplateStore
from smeagol.site.site import Site
from smeagol.utilities import filesystem as fs
from smeagol.widgets.styles.styles import Styles
from smeagol.utilities.types import Entry


class SystemInterface:
    def __init__(self, filename='', server=True, template_store=None):
        self.filename = filename
        self.styles = None
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
            case 'assets' | 'locations' | 'templates':
                return getattr(assets, attr.title())(self.config.get(attr, {}))
            case _default:
                try:
                    return super().__getattr__(attr)
                except AttributeError as e:
                    name = type(self).__name__
                    raise AttributeError(
                        f"'{name}' object has no attribute '{attr}'") from e

    def load_config(self, filename):
        try:
            return self._load_config_file(filename)
        except AttributeError:
            return self._create_config(filename)

    def setup(self, config):
        self.config = config
        self.open_styles()

    @property
    def entries(self) -> list[Entry]:
        entries = [self.find_entry(e) for e in self._entries]
        return entries or [self.site]

    @entries.setter
    def entries(self, entries: list[Entry]):
        self.config['entries'] = [entry.names for entry in entries]

    def find_entry(self, headings):
        return self.site[headings]

    def add_entry(self, entry: Entry) -> None:
        names = entry.names
        if names not in self._entries:
            self._entries.append(names)

    def remove_entry(self, entry: Entry) -> None:
        names = entry.names
        self._entries.remove(names)

    def open_styles(self):
        styles = self.config.get('styles', '')
        self.styles = Styles(fs.load_yaml(styles))

    def open_site(self):
        self._site_data = fs.load_yaml(self.assets.source)
        return Site(**self._site_data)

    @staticmethod
    def _load_config_file(filename):
        if filename.endswith('.smg'):
            return fs.load_yaml(filename)
        raise AttributeError('File type is Sméagol Source File. '
                             'Creating Sméagol Configuration File...')

    def save_config(self):
        if self.filename:
            fs.save_yaml(self.config, self.filename)

    def save_site(self):
        fs.save_yaml(self._site_data, self.assets.source)

    def open_entry_in_browser(self, entry):
        fs.open_in_browser(self.port, entry.link)
        return 'break'

    def save_entry(self, entry):
        self.template_store.set_data(entry, self.styles)
        html = self.template_store.main.html
        filename = os.path.join(
            self.locations.directory, *entry.link) + '.html'
        print('Saving', filename)
        fs.save_string(html, filename)

    def close_servers(self):
        fs.close_servers()
