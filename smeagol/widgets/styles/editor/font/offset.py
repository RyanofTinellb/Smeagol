import tkinter as tk
from tkinter import ttk


class Offset(ttk.LabelFrame):
    def __init__(self, parent, style):
        super().__init__(parent, text='offset')
        self.style = style
        for row, attr in enumerate(self.attrs):
            self.radio(attr).grid(row=row, column=0, sticky='w')
    
    @property
    def attrs(self):
        return 'superscript', 'baseline', 'subscript'
    
    def radio(self, attr):
        return tk.Radiobutton(self, **self.radio_options(attr))
    
    def radio_options(self, attr):
        return dict(
            text=attr,
            variable=self.style.offset,
            value=attr)