import tkinter as Tk
from .box import Box

class Frame(Tk.LabelFrame):
    def __init__(self, parent, style):
        super().__init__(parent, text='sample')
        Box(self, style).pack()