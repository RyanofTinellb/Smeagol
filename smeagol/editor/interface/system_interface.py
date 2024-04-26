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
                port=self.port, directory=self.locations.directory)

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

    @property
    def port(self):
        return self.config.get('port')

    @port.setter
    def port(self, value):
        self.config['port'] = value

    def load_from_config(self, attr, default_obj=None):
        return fs.load_yaml(self.config.get(attr, ''), default_obj)

    def create_from_config(self, obj: type, attr: str, default_obj=None) -> object:
        try:
            return obj(self.load_from_config(attr, default_obj))
        except AttributeError as e:
            filename = self.config.get(attr, '')
            raise AttributeError(f'{filename} is badly formatted. '
                                 'Please make a note of it.') from e

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
        self.styles = self.create_from_config(Styles, 'styles')

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
        fs.open_in_browser(self.port, entry.url)
        return 'break'

    def save_entry(self, entry):
        self.template_store.set_data(entry, self.styles)
        html = self.template_store.main.html
        filename = os.path.join(
            self.locations.directory, *entry.link) + '.html'
        fs.save_string(html, filename)
        print(f'Saving {filename}')

    def close_servers(self):
        fs.close_servers()

    def reopen_template_store(self):
        self.template_store = TemplateStore(self.templates)
