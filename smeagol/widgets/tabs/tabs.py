from tkinter import ttk

from smeagol.editor.interface.interfaces import Interfaces

class Tabs(ttk.Notebook):
    '''Keeps track of tabs and assigns Interfaces to them'''
    def __init__(self, parent):
        super().__init__(parent)
        self.interfaces = Interfaces()
        self.closed = []
    
    @property
    def commands(self):
        return [
            ('<<NotebookTabChanged>>', self.change_tab),
            ('<Button-2>', self.close_tab)
        ]

