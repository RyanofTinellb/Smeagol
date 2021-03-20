import tkinter as Tk
from tkinter import ttk
from .justify import Justify
from .spinner import Spinner

class Leftovers(Tk.Frame):
    def __init__(self, parent, style):
        super().__init__(parent, padx=10)
        self.style = style
        for row, var in enumerate(self.vars):
            Spinner(self, style, var).grid(row=row, column=1)
        self.set_labels()
        Justify(self, style).grid(row=2, column=1)
    
    def set_labels(self):
        labels = 'indent', 'line spacing', 'justification'
        for row, name in enumerate(labels):
            self.Label(name, row).grid(row=row, column=0, sticky='e')

    def Label(self, name, row):
        return ttk.Label(self, text=name, padding=(5, 0))
    
    @property
    def vars(self):
        return self.style.indent, self.style.line_spacing