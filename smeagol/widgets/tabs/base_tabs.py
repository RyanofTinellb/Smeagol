import tkinter as tk
from tkinter import ttk

from smeagol.editor.interface.interfaces import Interfaces
from smeagol.utilities import utils
from smeagol.utilities.types import Sidebar
from smeagol.widgets.tabs.tab import Tab


class BaseTabs(ttk.Notebook):
    '''Keeps track of tabs and assigns Interfaces to them'''

    def __init__(self, parent, textbox_commands, displays: Sidebar, title):
        super().__init__(parent)
        self.displays = displays
        self.change_title = title
        utils.bind_all(self, self.commands)
        self.textbox_commands = textbox_commands + self._textbox_commands
        self.interfaces = Interfaces()
        self.closed = []
        self.new()

    @property
    def commands(self):
        return [
            ('<<NotebookTabChanged>>', self.change),
            ('<Button-2>', self.close),
        ]

    @property
    def _textbox_commands(self):
        return ([
            ('<Control-t>', self.new),
            ('<Control-T>', self.reopen),
            ('<Control-w>', self.close),
        ])

    @property
    def current(self):
        return self.nametowidget(self.select())

    @property
    def textbox(self):
        return self.current.textbox

    @property
    def entry(self):
        return self.current.entry

    def new(self, _event=None):
        Tab(self, self.textbox_commands)
        self.update_displays()
        return 'break'

    def change(self, _event):
        self.update_displays()

    def close(self, event):
        tab = event.widget
        if self.index('end') - len(self.closed) <= 1:
            return None
        try:
            self._close(tab)
        except tk.TclError:
            self._close(self.select())
        self.update_displays()
        return 'break'

    def _close(self, tab):
        self.hide(tab)
        self.closed += [tab]

    def reopen(self, _event=None):
        with utils.ignored(IndexError):
            tab = self.closed.pop()
            self.add(tab)
            self.select(tab)
        self.update_displays()

    def update_displays(self):
        self.textbox.set_styles()
        self.textbox.update_styles()
        self.displays.update(self.textbox.displays)
        with utils.ignored(AttributeError):
            self.displays.headings = self.entry.names
            self.change_title(self.title)

    @property
    def title(self):
        return ' > '.join(self.entry.names)
