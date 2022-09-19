import tkinter as tk
from tkinter import ttk

from smeagol.utilities import utils
from smeagol.widgets.tabs.tab import Tab
from smeagol.editor.interface.interfaces import Interfaces


class Tabs(ttk.Notebook):
    '''Keeps track of tabs and assigns Interfaces to them'''
    def __init__(self, parent, textbox_commands):
        super().__init__(parent)
        utils.bind_all(self, self.commands)
        self.interfaces = Interfaces()
        self.closed = []
        self.textbox_commands = textbox_commands
        self.new()
    
    @property
    def current(self):
        return self.nametowidget(self.select())

    @property
    def title(self):
        return self.current.interface.site.root.name
    
    def open_sites(self, filenames=None):
        if not filenames:
            self.open_blank()
            return
        for i, filename in enumerate(filenames):
            self.open_site(filename, i)

    def open_site(self, filename, new_tab=True):
        interface = self.interfaces[filename]
        for i, entry in enumerate(interface.entries):
            # only open in same tab for first entry of first filename
            self.open_entry(interface, entry, new_tab + i)
    
    def open_entry(self, interface, entry, new_tab):
        if new_tab:
            self.new()
        self.current.interface = interface
        self.current.entry = entry

    def save_entry(self):
        entry = self.current.entry
        interface = self.current.interface
        text = self.current.text
        interface.save_entry(entry, text)
    
    def new(self):
        Tab(self, self.textbox_commands)

    def change(self, *_):
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

    def reopen(self, event=None):
        with utils.ignored(IndexError):
            tab = self.closed.pop()
            self.add(tab)
            self.select(tab)
        return 'break'
    
    @property
    def commands(self):
        return [
            ('<<NotebookTabChanged>>', self.change),
            ('<Button-2>', self.close)
        ]

