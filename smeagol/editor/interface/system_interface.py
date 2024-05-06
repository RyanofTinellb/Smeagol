import os

from smeagol.editor.interface import assets
from smeagol.editor.interface.templates.template_store import TemplateStore
from smeagol.site.site import Site
from smeagol.utilities import filesystem as fs
from smeagol.utilities.types import Entry
from smeagol.widgets.styles.styles import Styles


class SystemInterface:
    def __init__(self, filename='', server=True):
        self.filename = filename
        self.styles = None
        config = self.load_config(filename) if filename else {}
        self.setup(config)
        self.site = self.open_site()
        self.links = self.open_link_files(self._links)
        self.template_store = TemplateStore(self.templates, self.links)
        if server:
            self.port, self.handler = fs.start_server(
                port=self.port, directory=self.locations.directory)

    def __getattr__(self, attr):
        match attr:
            case 'site_info':
                value = self.config.setdefault('site', {})
            case '_entries':
                value = self.config.setdefault('entries', [[]])
            case 'assets' | 'locations' | 'templates':
                value = getattr(assets, attr.title())(
                    self.config.get(attr, {}))
            case 'serialisation_format':
                value = self.config.get('serialisation format', {}).copy()
            case '_links':
                value = self.config.setdefault('links', {})
            case _default:
                try:
                    value = super().__getattr__(attr)
                except AttributeError as e:
                    name = type(self).__name__
                    raise AttributeError(
                        f"'{name}' object has no attribute '{attr}'") from e
        return value

    def open_link_files(self, links: dict):
        return {key: fs.load_yaml(filename) for key, filename in links.items()}

    @property
    def port(self):
        return self.config.get('port')

    @port.setter
    def port(self, value):
        self.config['port'] = value

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

    def add_entry_to_config(self, entry: Entry) -> None:
        names = entry.names
        if names not in self._entries:
            self._entries.append(names)

    def remove_entry_from_config(self, entry: Entry) -> None:
        names = entry.names
        self._entries.remove(names)

    def add_entry_to_site(self, entry):
        self.site.add_entry(entry)

    def open_styles(self):
        styles = self.load_from_config('styles')
        imes = {name: fs.load_yaml(filename)
                for name, filename in self._imes.items()}
        try:
            self.styles = Styles(styles, imes)
        except AttributeError as e:
            filename = self.config.get('styles', '')
            raise AttributeError(f'{filename} is badly formatted. '
                                 'Please make a note of it.') from e

    def load_from_config(self, attr, default_obj=None):
        return fs.load_yaml(self.config.get(attr, ''), default_obj)

    def open_site(self):
        self._site_data = fs.load_yaml(self.assets.source)
        return Site(**self._site_data,
                    serialisation_format=self.serialisation_format)

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

    def save_entries(self):
        total = len(self.site)
        percent = each = 5
        for i, entry in enumerate(self.site):
            if 100*i/total >= percent:
                yield 100*i // total
                percent += each
            self.save_entry(entry)
        yield 100

    def save_entry(self, entry):
        self.template_store.set_data(entry, self.styles)
        try:
            html = self.template_store.main.html
        except (ValueError, IndexError) as e:
            raise type(e)(f'Incorrect formatting in entry {entry.name}') from e
        filename = os.path.join(
            self.locations.directory, entry.url)
        fs.save_string(html, filename)
        return filename

    def save_special_files(self):
        if not self.template_store.page:
            return
        self.save_searchfile()
        self.save_search404_file()
        self.save_search_data()
        if self.serialisation_format:
            self.save_wordlist()

    def save_searchfile(self):
        html = self.template_store.search.html
        filename = self.locations.search
        fs.save_string(html, filename)

    def save_search404_file(self):
        html = self.template_store.page404.html
        self.handler.error_message_format = html
        filename = self.locations.page404
        fs.save_string(html, filename)

    def save_search_data(self):
        data = self.site.analysis()
        filename = self.assets.searchindex
        fs.save_json(data, filename)

    def save_wordlist(self):
        data = self.site.serialisation()
        filename = self.assets.wordlist
        fs.save_json(data, filename, indent=2)

    def close_servers(self):
        fs.close_servers()

    def reopen_template_store(self):
        self.template_store = TemplateStore(self.templates)
