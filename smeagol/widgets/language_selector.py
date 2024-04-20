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
        self.update = True

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
        if not self.update or not self.names:
            return
        self.update = False
        name = self.names[self.code.get()]
        if name != self.name.get():
            self.name.set(name)
        self.update = True

    def update_code(self, *_args):
        if not self.update:
            return
        self.update = False
        code = self.codes[self.name.get()]
        if code != self.code.get():
            self.code.set(code)
        self.update = True

    def config(self, *args, **kwargs):
        self.code: tk.StringVar = kwargs.pop('textvariable', None) or self.code
        with utils.ignored(AttributeError):
            self.code.trace_add('write', self.update_name)
        super().config(*args, **kwargs)
