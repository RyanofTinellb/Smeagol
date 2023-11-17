import tkinter as tk

from .direction import Direction
from .leftovers import Leftovers
from .units import Units


class Frame(tk.LabelFrame):
    def __init__(self, parent, style):
        super().__init__(parent, text='paragraph')
        Leftovers(self, style).grid(row=0, column=0)
        Direction(self, style).grid(row=0, column=1)
        Units(self, style).grid(row=1, column=0, columnspan=2)