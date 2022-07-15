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
        self.new(self.interfaces.blank)
    
    @property
    def current(self):
        return self.nametowidget(self.select())

    @property
    def title(self):
        return self.current.interface.site.root.name
    
    def open_site(self, filename=''):
        try:
            self.interface = self.interfaces[filename]
        except AttributeError:  # filename is a list
            self.interface = self.open_sites(filename)

    def open_sites(self, filenames):
        first_tab = True
        for filename in filenames:
            interface = self.interfaces[filename]
            self.open_interface(interface, first_tab)
            self.current.textbox.styles = interface.styles
            first_tab = False
        return interface
    
    def open_interface(self, interface, first_tab=False):
        for entry in interface.entries:
            self.open(entry, first_tab)
    
    def new(self, interface=None):
        interface = interface or self.current.interface
        Tab(self, interface, self.textbox_commands)
    
    def open(self, entry, first_tab=False):
        if not first_tab:
            self.new()

    def change(self, event=None):
        self.current.textbox.set_styles()

    def close(self, event):
        print(self.index('end'), len(self.closed))
        if self.index('end') - len(self.closed) <= 1:
            return
        tab = f'@{event.x},{event.y}'
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

