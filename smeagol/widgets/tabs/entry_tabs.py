from smeagol.widgets.tabs.base_tabs import BaseTabs


class EntryTabs(BaseTabs):
    def save_all(self):
        pass

    @property
    def title(self):
        return self.current.interface.site.root.name

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
