from smeagol.utilities import utils
from smeagol.widgets.tabs.base_tabs import BaseTabs
from smeagol.utilities.types import Page


class Tabs(BaseTabs):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

    @property
    def headings(self):
        return self.displays.headings

    def open_sites(self, filenames=None):
        if not filenames:
            # self.open_blank()
            return
        for i, filename in enumerate(filenames):
            self.open_site(filename, i)

    def open_site(self, filename, new_tab=True):
        interface = self.interfaces[filename]
        for i, entry in enumerate(interface.entries):
            self._open_site(interface, entry, new_tab + i, filename)

    def _open_site(self, interface, entry, new_tab, filename):
        # only open in same tab for first entry of first filename
        try:
            self.open_entry(interface, entry, new_tab)
        except TypeError as e:
            raise TypeError(f'Unable to load from {filename}') from e

    def open_entry(self, interface=None, entry: Page=None, new_tab=False):
        if new_tab:
            self.new()
        self.current.interface = interface or self.interface
        try:
            self.current.entry = entry
        except (KeyError, IndexError):
            self.current.interface.add_entry_to_site(entry)
            self.current.entry = entry
        self.update_displays()
        self.interface.add_entry_to_config(entry)

    def previous_entry(self, event):
        print('giraffe')
        entry = event.widget.level
        with utils.ignored(IndexError):
            self.displays.headings = entry.previous_sister.names
        return 'break'

    def next_entry(self, event):
        entry = self.entry[self.displays.headings[:event.widget.level + 1]]
        try:
            entry = entry.next_sister
        except IndexError:
            with utils.ignored(IndexError):
                entry = entry.eldest_daughter
        self.displays.headings = entry.names
        return 'break'

    def load_entry(self, event):
        try:
            self.open_entry(entry=self.entry.new(
                self.displays.headings[:event.widget.level + 1]))
        except IndexError:
            self.textbox.focus_set()
            self.textbox.see('insert')
        heading = self.displays.add_heading()
        if heading:
            heading.focus_set()

    def update_language(self, _event=None):
        self.interface.styles.language_code = self.displays.language_selector.get()
        self.textbox.focus_set()

    @property
    def headings_commands(self):
        return [
            ('<Prior>', self.previous_entry),
            ('<Next>', self.next_entry),
            ('<Return>', self.load_entry),
        ]

    @property
    def language_commands(self):
        return [
            ('<<ComboboxSelected>>', self.update_language)
        ]
