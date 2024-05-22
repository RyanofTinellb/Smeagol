import tkinter as tk
from tkinter import ttk
from smeagol.utilities import utils


class LanguageSelector(ttk.Combobox):
    def __init__(self, parent):
        self.names = self.codes = self.code = None
        self.name = tk.StringVar()
        self.name.trace_add('write', self.update_code)
        self._commands = []
        super().__init__(parent, height=2000, width=25,
                         justify=tk.CENTER, textvariable=self.name)
        self.state(['readonly'])

    @property
    def commands(self):
        return self._commands

    @commands.setter
    def commands(self, commands):
        self._commands = commands
        for key, command in commands:
            self.bind(f'{key}', command)

    def get(self):
        return self.code.get()

    @property
    def languages(self):
        return self.names

    @languages.setter
    def languages(self, languages):
        if not languages:
            return
        self.names = languages
        self.codes = {name: code for code, name in languages.items()}
        values = list(self.names.values())
        self.config(values=values)
        if not self.name.get():
            self.name.set(values[0])

    def update_name(self, *_args):
        if not self.names:
            return
        code = self.code.get()
        name = self.names[code] if code and code != 'None' else ''
        if not name or name == self.name.get():
            return
        self.name.set(name)

    def update_code(self, *_args):
        code = self.codes[name] if (name := self.name.get()) else ''
        if not code or code == self.code.get():
            return
        self.code.set(code)

    def config(self, *args, **kwargs):
        self.code: tk.StringVar = kwargs.pop('textvariable', None) or self.code
        self.code.set('')
        with utils.ignored(AttributeError):
            self.code.trace_add('write', self.update_name)
        super().config(*args, **kwargs)
