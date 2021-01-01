import tkinter as Tk
from .interface import Interface
from ..widgets import Textbox


class Tab(Tk.Frame):
    def __init__(self, master=None, interface=None, entry=None):
        super().__init__(master)
        self.notebook = master
        self.notebook.add(self)
        self.notebook.select(self)
        self.interface = interface or Interface()
        self.textbox = self._textbox
        self.entry = entry or self.interface.site.root

    @property
    def _textbox(self):
        styles = self.interface.styles
        translator = self.interface.translator
        textbox = Textbox(self, styles, translator)
        textbox.pack(side=Tk.LEFT, expand=True, fill=Tk.BOTH)
        return textbox
    
    @property
    def entry(self):
        return self._entry
    
    @entry.setter
    def entry(self, entry):
        self._entry = entry
        self.textbox.text = self.interface.styles.hide_tags(str(self.entry))
        self.name = self.entry.name
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        self.notebook.tab(self, text=name)
    

