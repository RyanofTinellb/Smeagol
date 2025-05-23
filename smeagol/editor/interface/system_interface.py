import os
import re

from smeagol.editor.interface import assets
from smeagol.editor.interface.templates.template_store import TemplateStore
from smeagol.site.site import Site
from smeagol.utilities import filesystem as fs
from smeagol.utilities import utils
from smeagol.utilities.types import Entry
from smeagol.widgets.styles.styles import Styles


class SystemInterface:
    def __init__(self, filename='', server=True):
        self.filename = filename
        self.styles = self.files = self.links = self.template_store = None
        config = self.load_config(filename) if filename else {}
        self.setup(config)
        self.site = self.open_site()
        self.open_assets()
        self.start_server(server)

    def start_server(self, server):
        page404location = self.locations.page404
        page404 = fs.load_string(page404location) if page404location else ''
        if server:
            self.port, self.handler = fs.start_server(
                port=self.port, page404=page404, directory=self.locations.directory)

    def __getattr__(self, attr):
        match attr:
            case 'site_info':
                value = self.config.setdefault('site', {})
            case '_entries':
                value = self.config.setdefault('entries', [[]])
            case '_files':
                value = self.config.get('files', '')
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
        self.open_files()

    def open_files(self):
        self.files = fs.load_yaml(self._files)

    def copy_all(self):
        fs.copy_all(self.files)

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

    def save_site(self, filename=None):
        filename = filename or self.assets.source
        fs.save_yaml(self._site_data, filename)

    def open_entry_in_browser(self, entry):
        fs.open_in_browser(self.port, entry.url)
        return 'break'

    def save_entries(self):
        total = len(self.site)
        percent = each = 5
        for i, entry in enumerate(reversed(list(self.site))):
            if 100*i/total >= percent:
                yield 100*i // total
                percent += each
            filename, saved = self.save_entry(entry)
            if not saved:
                print(f'Deleting {filename}')
        yield 100

    def save_entry(self, entry, copy_all=False):
        filename = os.path.join(
            self.locations.directory, entry.url)
        with utils.ignored(IndexError):
            self.site.remove_entry(entry)
            fs.delete_file(filename)
            return (filename, False)
        try:
            html = self.template_store.html(entry)
        except (ValueError, IndexError, TypeError) as e:
            raise type(e)(f'Incorrect formatting in entry {entry.name}') from e
        fs.save_string(html, filename)
        if copy_all:
            self.copy_all()
        return (filename, True)

    def save_special_files(self):
        for (item, html) in self.template_store.special_files(self.site):
            if item == 'search404':
                self.handler.error_message_format = html
            try:
                fs.save_string(html, self.locations[item])
            except KeyError as e:
                message = f'Error saving {item} for {self.filename}'
                raise ValueError(message) from e
        try:
            self.save_search_data()
            if self.serialisation_format:
                self.save_wordlist()
        except ValueError as e:
            message = f'Error saving special files of {self.filename}'
            raise ValueError(message) from e

    def _page(self, filename: str):
        name = os.path.relpath(filename, self.locations.directory)
        name, _ext = os.path.splitext(name)
        name = re.split(r'[/\\]+', name)
        name = [self.site.name, *name]
        return self.site.new(name)

    def save_search_data(self):
        data = self.site.analysis()
        filename = self.assets.searchindex
        fs.save_json(data, filename)

    def save_wordlist(self):
        data = sorted(self.site.serialisation(), key=lambda x: x['t'])
        filename = self.assets.wordlist
        fs.save_json(data, filename)

    def close_servers(self):
        fs.close_servers()

    def open_assets(self):
        self.links = self.open_link_files(self._links)
        self.template_store = TemplateStore(
            self.templates, self.links, self.styles)
