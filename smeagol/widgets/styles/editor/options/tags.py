import tkinter as tk
from tkinter import ttk


class Tags(ttk.Labelframe):
    def __init__(self, parent, style):
        super().__init__(parent, text='tags')
        self.style = style
        for row, (entry, var) in enumerate(self.boxes):
            tk.Entry(self, textvar=var, width=30).grid(row=row, column=0)

    @property
    def boxes(self):
        return (
            ('start', self.style.start),
            ('end', self.style.end))
