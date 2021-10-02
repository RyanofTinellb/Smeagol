from tkinter import ttk
from tkinter.font import families
from .offset import Offset
from .styling import Styling


class Frame(ttk.LabelFrame):
    def __init__(self, parent, style):
        super().__init__(parent, text='font')
        self.style = style
        self.family_box.grid(row=0, column=0)
        self.size_box.grid(row=0, column=1)
        Styling(self, style).grid(row=1, column=0, sticky='w')
        Offset(self, style).grid(row=1, column=1)

    @property
    def family_box(self):
        return ttk.Combobox(self, **self.family_options)
    
    @property
    def family_options(self):
        return dict(
            width=20, textvariable=self.style.font,
            values=sorted([''] + [f for f in families() if not f.startswith('@')]))
        
    @property
    def size_box(self):
        return ttk.Spinbox(self, **self.size_options)

    @property
    def size_options(self):
        return dict(
            width=5, from_=1, to=72,
            textvariable=self.style.size)