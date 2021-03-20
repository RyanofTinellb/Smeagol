import tkinter as Tk
from tkinter import ttk

class Units(ttk.LabelFrame):
    def __init__(self, parent, style):
        super().__init__(parent, text='units')
        self.style = style
        self.Selector.grid(row=0, column=1)

    @property
    def Selector(self):
        return ttk.Combobox(self, **self.selector_options)
    
    @property
    def selector_options(self):
        return dict(
            state=self.style.state.get() or 'readonly',
            textvariable=self.style.unit,
            values=self.units)
    
    @property
    def units(self):
        return 'points', 'millimetres', 'centimetres', 'inches'