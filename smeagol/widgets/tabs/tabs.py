import tkinter as tk
from tkinter import ttk

from smeagol.utilities import utils
from smeagol.widgets.tabs.tab import Tab
from smeagol.editor.interface.interfaces import Interfaces

class Tabs(ttk.Notebook):
    '''Keeps track of tabs and assigns Interfaces to them'''
    def __init__(self, parent):
        super().__init__(parent)
        self.interfaces = Interfaces()
        self.closed = []
    
    @property
    def current(self):
        return self.nametowidget(self.tabs.select())
    
    def open_site(self, filename=''):
        try:
            self.interface = self.interfaces[filename]
        except AttributeError:  # filename is a list
            self.interface = self.open_sites(filename)

    def open_sites(self, filenames):
        first_tab = True
        for filename in filenames:
            interface = self.interfaces[filename]
            self.textbox.styles = interface.styles
            self.open_interface(interface, first_tab)
            first_tab = False
        return interface
    
    def new_tab(self, interface=None):
        interface = interface or self.interface
        Tab(self.tabs, interface)
        self._bind_all(self.textbox, self.textbox_commands)
        return 'break'
    
    def open_tab(self, entry, first_tab=False):
        if not first_tab:
            self.new_tab()
        self.open_entry(entry)

    def change_tab(self, event=None):
        self.update_displays()
        self.change_language()
        self.textbox.set_styles()
        self.set_headings(self.entry)
        self.title = self.interface.site.root.name

    def close_tab(self, event=None):
        if self.tabs.index('end') - len(self.closed_tabs) > 1:
            tab = f'@{event.x},{event.y}'
            while True:
                try:
                    self.tabs.hide(tab)
                    self.closed_tabs += [tab]
                    break
                except tk.TclError:
                    tab = self.tabs.select()
        return 'break'

    def reopen_tab(self, event=None):
        with utils.ignored(IndexError):
            tab = self.closed_tabs.pop()
            self.tabs.add(tab)
            self.tabs.select(tab)
        return 'break'
    
    @property
    def commands(self):
        return [
            ('<<NotebookTabChanged>>', self.change_tab),
            ('<Button-2>', self.close_tab)
        ]

