import tkinter as tk

from smeagol.utilities import utils

from smeagol.widgets.textbox.textbox import Textbox


# pylint: disable=R0902


class Tab(tk.Frame):
    def __init__(self, parent, commands: list[tuple], clipboard):
        super().__init__(parent)
        self.notebook = parent
        self.notebook.add(self)
        self.notebook.select(self)
        self.clipboard = clipboard
        self.commands = self._commands + commands
        self.textbox = self._textbox()
        self.is_open = True

    def _textbox(self):
        textbox = Textbox(self.clipboard, self)
        textbox.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        utils.bind_all(textbox, self.commands)
        return textbox

    @property
    def _commands(self):
        return [
            ('<Control-s>', self.save_entry),
            ('<Control-S>', self.save_entries),
            ('<Control-Prior>', self.previous_entry),
            ('<Control-Next>', self.next_entry)
        ]

    def go_to_headings(self, _event=None):
        self.notebook.go_to_headings()

    def save_entry(self, _event=None):
        self.entry.text = self.textbox.text
        self.entry.title = self.textbox.title
        self.entry.update_date()
        self.entry.position = self.textbox.index('insert')
        self.interface.save_site()
        filename, saved = self.interface.save_entry(self.entry, True)
        # saved? = file saved rather than deleted
        message = 'Saving' if saved else 'Deleting'
        print(f'{message} {filename}')
        return 'break'

    def save_entries(self, _event=None):
        for percentage in self.interface.save_entries():
            print(f'{percentage}% complete')
        self.interface.save_site()
        self.interface.save_special_files()

    def previous_entry(self, _event=None):
        self.entry = self.entry.previous_page()

    def next_entry(self, _event=None):
        self.entry = self.entry.next_page()

    @property
    def entry(self):
        return self._entry

    @entry.setter
    def entry(self, entry):
        self._entry = entry
        self.name = self.entry.name
        self.textbox.title = entry.title or utils.default_title(entry)
        self.textbox.text = entry.text
        self.textbox.mark_set('insert', self.entry.position)
        self.textbox.see('insert')
        self.textbox.focus_set()
        self.textbox.get_styles_from_cursor()

    @property
    def interface(self):
        return self._interface

    @interface.setter
    def interface(self, interface):
        self._interface = interface
        self.textbox.styles = interface.styles
        self.textbox.ime = interface.styles.imes.get(
            interface.styles['default'].ime, {})
        self.textbox.languages = interface.languages

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
        self.notebook.tab(self, text=name)

    def open(self):
        self.is_open = True

    def close(self):
        self.is_open = False
