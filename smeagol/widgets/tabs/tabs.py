from smeagol.utilities import utils
from smeagol.widgets.tabs.base_tabs import BaseTabs
from smeagol.editor.interface.interfaces import Interfaces
from smeagol.utilities.types import Page
from typing import Optional


class Tabs(BaseTabs):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.interfaces = Interfaces()
        self.displays.headings_frame.commands = self.headings_commands
        self.displays.language_selector.commands = self.language_commands

    def save_all(self):
        tabs = utils.groupby(
            [self.nametowidget(tab) for tab in self.tabs()],
            lambda name: self.nametowidget(name).interface.filename)
        for interface, tab_group in tabs:
            self.interfaces[interface].entries = [
                tab.entry for tab in tab_group if tab.is_open]
        self.interfaces.save_all()

    def save_all_entries(self):
        self.interfaces.save_all_entries()

    @property
    def headings(self):
        return self.displays.headings

    def open_sites(self, filenames=None, new_tab=False):
        if not filenames:
            # self.open_blank()
            return
        for i, filename in enumerate(filenames, start=new_tab):
            self.open_site(filename, bool(i))

    def open_site(self, filename, new_tab=True):
        interface = self.interfaces[filename]
        if not interface:
            return
        for i, entry in enumerate(interface.entries):
            self._open_site(interface, entry, new_tab + i, filename)

    def _open_site(self, interface, entry, new_tab, filename):
        # only open in same tab for first entry of first filename
        try:
            self.open_entry(interface, entry, new_tab)
        except TypeError as e:
            raise TypeError(f'Unable to load from {filename}') from e

    def open_entry(self, interface=None, entry: Optional[Page] = None, new_tab=False, switch_tab=True):
        interface = interface or self.interface
        current = self.current
        if new_tab:
            self.new()
        self.interface = interface
        try:
            self.current.entry = entry
        except (KeyError, IndexError):
            self.add_new(entry)
        self.update_displays()
        self.interface.add_entry_to_config(entry)
        if not switch_tab:
            self.select(current)

    def add_new(self, entry):
        self.current.interface.add_entry_to_site(entry)
        try:
            self.current.entry = entry
        except IndexError as e:
            raise IndexError(f'Bad formatting in {entry.name}') from e

    def previous_sister(self, event):
        entry = self.entry[self.displays.headings[:event.widget.level + 1]]
        with utils.ignored(IndexError):
            self.displays.headings = entry.previous_sister().names
        return 'break'

    def next_sister(self, event):
        entry = self.entry[self.displays.headings[:event.widget.level + 1]]
        with utils.ignored(IndexError):
            self.displays.headings = entry.next_sister().names
        return 'break'

    def load_entry(self, event):
        if not event.widget.get():
            self.textbox.focus_set()
            return
        try:
            self.open_entry(entry=self.entry.new(
                self.displays.headings[:event.widget.level + 1]))
        except IndexError:
            self.textbox.focus_set()
        heading = self.displays.add_heading()
        if heading:
            heading.focus_set()

    def update_language(self, _event=None):
        self.interface.styles.language_code = self.displays.language_selector.get()
        self.textbox.focus_set()

    def follow_link(self, link):
        link = link.split('#')[0].split('/')
        if not link[0]:
            if link[-1].endswith('.html'):
                link[-1] = link[-1].removesuffix('.html')
            if link[-1].lower() == 'index':
                link.pop()
            link[0] = self.entry.root.name
            self.open_entry(entry=self.entry.new(link), new_tab=True, switch_tab=False)

    @property
    def _textbox_commands(self):
        return super()._textbox_commands + [
            ('<<FollowLink>>', self.follow_link)
        ]
    
    @property
    def headings_commands(self):
        return [
            ('<Prior>', self.previous_sister),
            ('<Next>', self.next_sister),
            ('<Return>', self.load_entry),
        ]

    @property
    def language_commands(self):
        return [
            ('<<ComboboxSelected>>', self.update_language)
        ]
