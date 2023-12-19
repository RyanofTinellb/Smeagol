import tkinter as tk

from smeagol.utilities import utils
from smeagol.conversion import api as conversion

from smeagol.widgets.textbox.textbox import Textbox


class Tab(tk.Frame):
    def __init__(self, parent, commands):
        super().__init__(parent)
        self.notebook = parent
        self.notebook.add(self)
        self.notebook.select(self)
        self.textbox = self._textbox(commands)

    def _textbox(self, commands):
        textbox = Textbox(self)
        textbox.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        utils.bind_all(textbox, commands)
        return textbox

    @property
    def entry(self):
        return self._entry

    @entry.setter
    def entry(self, entry):
        self._entry = entry
        self.name = self.entry.name
        self.textbox.text = self.entry_text

    @property
    def interface(self):
        return self._interface

    @interface.setter
    def interface(self, interface):
        self._interface = interface
        self.textbox.translator = interface.translator
        self.textbox.styles = interface.styles

    @property
    def entry_text(self):
        text = self._entry.text
        return conversion.TextTree(text)

    @property
    def text(self):
        text = self.textbox.formatted_text
        return conversion.TextTree(text)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
        self.notebook.tab(self, text=name)
