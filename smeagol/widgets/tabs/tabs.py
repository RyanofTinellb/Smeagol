from smeagol.utilities import utils
from smeagol.widgets.tabs.base_tabs import BaseTabs


class Tabs(BaseTabs):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.displays.headings_frame.commands = self.headings_commands

    def save_all(self):
        pass

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
        for i, entry in enumerate(interface.entries()):
            # only open in same tab for first entry of first filename
            self.open_entry(interface, entry, new_tab + i)

    def open_entry(self, interface=None, entry=None, new_tab=False):
        # pylint: disable=W0201
        if new_tab:
            self.new()
        self.current.interface = interface or self.interface
        self.current.entry = entry or entry
        self.update_displays()

    def previous_entry(self, event):
        print('giraffe')
        entry = (event.widget.level)
        with utils.ignored(IndexError):
            self.displays.headings = entry.previous_sister.names
        return 'break'

    def next_entry(self, event):
        entry = (event.widget.level)
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

    @property
    def headings_commands(self):
        return [
            ('<Prior>', self.previous_entry),
            ('<Next>', self.next_entry),
            ('<Return>', self.load_entry),
        ]
