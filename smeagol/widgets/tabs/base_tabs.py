import tkinter as tk
from tkinter import ttk

from smeagol.editor.interface.interfaces import Interfaces
from smeagol.utilities import utils
from smeagol.widgets.tabs.tab import Tab


class BaseTabs(ttk.Notebook):
    '''Keeps track of tabs and assigns Interfaces to them'''

    def __init__(self, parent, textbox_commands):
        super().__init__(parent)
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

    def new(self, _event=None):
        Tab(self, self.textbox_commands)
        return 'break'

    def change(self, _event):
        self.current.textbox.set_styles()

    def close(self, tab):
        if self.index('end') - len(self.closed) <= 1:
            return
        try:
            self._close(tab)
        except tk.TclError:
            self._close(self.select())

    def _close(self, tab):
        self.hide(tab)
        self.closed += [tab]

    def reopen(self, _event=None):
        with utils.ignored(IndexError):
            tab = self.closed.pop()
            self.add(tab)
            self.select(tab)
        return 'break'
