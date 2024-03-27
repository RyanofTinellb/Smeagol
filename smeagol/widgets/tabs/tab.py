import tkinter as tk

from smeagol.utilities import utils

from smeagol.widgets.textbox.textbox import Textbox


class Tab(tk.Frame):
    def __init__(self, parent, commands: list[tuple]):
        super().__init__(parent)
        self.notebook = parent
        self.notebook.add(self)
        self.notebook.select(self)
        self.commands = self._commands + commands
        self.textbox = self._textbox()

    def _textbox(self):
        textbox = Textbox(self)
        textbox.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        utils.bind_all(textbox, self.commands)
        return textbox

    @property
    def _commands(self):
        return [
            ('<Control-s>', self.save_entry)
        ]

    def save_entry(self, _event=None):
        self.entry.text = self.textbox.text
        # self.interface.save_site()
        self.interface.save_entry(self.entry)
        return 'break'

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
        return self._entry.text

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
        self.notebook.tab(self, text=name)
