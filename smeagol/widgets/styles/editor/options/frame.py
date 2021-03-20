import tkinter as Tk
from tkinter import ttk

from .key import Key
from .block import Block
from .tags import Tags


class Frame(ttk.LabelFrame):
    def __init__(self, parent, style):
        super().__init__(parent, text='options')
        self.style = style
        Block(self, style).grid(row=0, column=0, sticky='w')
        Key(self, style).grid(row=1, column=0, sticky='w')
        Tags(self, style).grid(row=2, column=0, sticky='w')
        for row, (attr, var) in enumerate(self.buttons, start=3):
            Tk.Checkbutton(self, text=attr, var=var).grid(row=row, column=0, sticky='w')
    
    @property
    def buttons(self):
        return (
            ('language', self.style.language),
            ('hyperlink', self.style.hyperlink))