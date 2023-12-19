import re
import tkinter as tk


class Key(tk.Frame):
    def __init__(self, parent, style):
        super().__init__(parent)
        self.style = style
        self.Label.grid(row=0, column=0, sticky='e')
        self.Box.grid(row=0, column=1, padx=10)

    @property
    def Box(self):
        box = tk.Entry(self, **self.box_options)
        box.bind('<KeyPress>', self.change_key)
        return box

    @property
    def box_options(self):
        return dict(
            width=2,
            justify='center',
            textvariable=self.style.key)

    def change_key(self, event):
        if event.keysym == 'Return':
            return 'break'
        char = event.char
        key = char if re.match(r'[a-zA-Z]', char) else ''
        self.style.key.set(key)
        return 'break'

    @property
    def Label(self):
        return tk.Label(self, text='key', justify='right')
