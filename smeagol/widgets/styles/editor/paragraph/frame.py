import tkinter as Tk
from .leftovers import Leftovers
from .direction import Direction
from .units import Units


class Frame(Tk.LabelFrame):
    def __init__(self, parent, style):
        super().__init__(parent, text='paragraph')
        Leftovers(self, style).grid(row=0, column=0)
        Direction(self, style).grid(row=0, column=1)
        Units(self, style).grid(row=1, column=0, columnspan=2)