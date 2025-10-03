import tkinter as tk
from tkinter import ttk

from smeagol.utilities import utils
from smeagol.utilities.types import Sidebar
from smeagol.widgets.tabs.tab import Tab


class BaseTabs(ttk.Notebook):
    '''Keeps track of tabs and assigns Interfaces to them'''

    def __init__(self, parent, textbox_commands, displays: Sidebar, title):
        super().__init__(parent)
        self.styles_menu = None
        self.displays = displays
        self.change_title = title
        self.add_commands(self.commands)
        self.textbox_commands = textbox_commands + self._textbox_commands
        self.clipboard = utils.Clipboard()
        self.closed = []
        self.new()

    def add_commands(self, commands):
        for keys, command in commands:
            if isinstance(keys, str):
                self.bind(keys, command)
            else:
                for key in keys:
                    self.bind(key, command)

    @property
    def commands(self):
        return [
            ('<<NotebookTabChanged>>', self.change),
            ('<Button-2>', self.close),
        ]

    @property
    def _textbox_commands(self):
        return ([
            ('<Control-t>', self.create),
            ('<Control-T>', self.reopen),
            ('<Control-w>', self.close),
            ('<Alt-d>', self.go_to_headings),
            ('<Enter>', self.update_displays),
            ('<F5>', self.reload_from_files)
        ])

    def go_to_headings(self, _event=None):
        self.displays.go_to_headings()
        return 'break'

    def reload_from_files(self, _event=None):
        self.reload_styles()
        self.reload_assets()

    def reload_styles(self, _event=None):
        self.interface.open_styles()
        self.interface.styles.language_code = self.textbox.styles.language_code
        self.textbox.styles = self.interface.styles
        self.textbox.configure_tags()
        self.textbox.clear_styles_menu()

    def reload_assets(self, _event=None):
        # reloads links and template_store
        self.interface.open_assets()

    @property
    def current(self):
        return self.nametowidget(self.select())

    @property
    def textbox(self):
        return self.current.textbox

    @property
    def interface(self):
        return self.current.interface

    @interface.setter
    def interface(self, interface):
        self.current.interface = interface

    @property
    def entry(self):
        return self.current.entry

    @entry.setter
    def entry(self, entry):
        self.current.entry = entry

    def new(self, _event=None):
        Tab(self, self.textbox_commands, self.clipboard)
        self.update_displays()
        return 'break'

    def create(self, _event=None):
        interface = self.interface
        entry = self.entry
        self.new()
        self.interface = interface
        self.entry = entry
        # self.update_displays()
        self.go_to_headings()
        return 'break'

    def change(self, _event):
        self.update_displays()
        self.textbox.get_styles_from_cursor()
        # self.go_to_headings()

    def close(self, event):
        try:
            current = self.select()
            self.select(self.index(f'@{event.x},{event.y}'))
            source = None if current == self.select() else current
        except tk.TclError:
            source = None
        if len(self.interface_tabs) <= 1:
            return 'break'
        self._close(self.select())
        self.select(source)
        self.update_displays()
        return 'break'

    @property
    def interface_tabs(self):
        tabs = [self.nametowidget(tab) for tab in self.tabs()]
        return [tab for tab in tabs if tab.interface == self.interface
                and tab.is_open]

    def _close(self, tab):
        self.nametowidget(tab).close()
        self.hide(tab)
        self.closed += [tab]

    def reopen(self, _event=None):
        with utils.ignored(IndexError):
            tab = self.closed.pop()
            self.nametowidget(tab).open()
            self.add(tab)
            self.select(tab)
        self.update_displays()

    def update_displays(self, _event=None):
        self.textbox.configure_tags(self.styles_menu)
        self.displays.languages = self.textbox.languages
        self.displays.update(self.textbox.displays)
        with utils.ignored(AttributeError):
            self.displays.headings = self.entry.names
            self.change_title(self.title)

    @property
    def title(self):
        return ' > '.join(self.entry.names)
