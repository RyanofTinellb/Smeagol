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

    def open_entry(self, interface, entry, new_tab):
        # pylint: disable=W0201
        if new_tab:
            self.new()
        self.current.interface = interface
        self.current.entry = entry
        self.update_displays()

    def _entry(self, level):
        return self.current.interface.find_entry(self.displays.headings[:level+1])

    def previous_entry(self, event):
        print('giraffe')
        entry = self._entry(event.widget.level)
        with utils.ignored(IndexError):
            self.displays.headings = entry.previous_sister.names
        return 'break'

    def next_entry(self, event):
        entry = self._entry(event.widget.level)
        try:
            entry = entry.next_sister
        except IndexError:
            with utils.ignored(IndexError):
                entry = entry.eldest_daughter
        self.displays.headings = entry.names
        return 'break'

    def load_entry(self, event):
        # pylint: disable=W0201
        self.entry = self._entry(event.widget.level)
        try:
            self.displays.headings = self.entry.eldest_daughter
            self.displays.headings.select_last()
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
