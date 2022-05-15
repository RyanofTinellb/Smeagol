import tkinter as tk
from .textbox import Textbox


class Tab(tk.Frame):
    def __init__(self, parent, interface, entry=None):
        super().__init__(parent)
        self.notebook = parent
        self.notebook.add(self)
        self.notebook.select(self)
        self.interface = interface
        self.textbox = self._textbox
        self.entry = entry or self.interface.site.root

    @property
    def _textbox(self):
        styles = self.interface.styles
        translator = self.interface.translator
        textbox = Textbox(self, styles, translator)
        textbox.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        return textbox
    
    @property
    def entry(self):
        return self._entry
    
    @entry.setter
    def entry(self, entry):
        self._entry = entry
        self.textbox.styles = self.interface.styles
        self.textbox.text = self.entry_text
        self.name = self.entry.name
    
    @property
    def entry_text(self):
        text = self._entry.text
        hidden_tags = self.interface.styles.hide_tags
        return hidden_tags(text)
    
    @property
    def text(self):
        text = self.textbox.formatted_text
        show_tags = self.interface.styles.show_tags
        return show_tags(text)
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        self._name = name
        self.notebook.tab(self, text=name)
    

