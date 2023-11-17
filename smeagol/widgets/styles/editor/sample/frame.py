import tkinter as tk

from .box import Box


class Frame(tk.LabelFrame):
    def __init__(self, parent, style):
        super().__init__(parent, text='sample')
        Box(self, style).pack()