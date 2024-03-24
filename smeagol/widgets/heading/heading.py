import tkinter as tk


class Heading(tk.Entry):
    def __init__(self, level, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.level = level

    def bind_commands(self, commands):
        for key, command in commands:
            self.bind(f'{key}', command)

    def set(self, value=''):
        self.delete(0, 'end')
        self.insert(0, value)

    def grid(self, *args, **kwargs):
        super().grid(*args, **kwargs)
        return self
