import tkinter as tk
from tkinter import Variable
from tkinter import ttk
from typing import Optional


from smeagol.conversion import api as conversion
from smeagol.utilities.utils import ignored
from smeagol.widgets.heading.heading_frame import HeadingFrame


class Sidebar(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.headings_frame = self.create_headings(self)
        self.displays = {
            'wordcount': tk.Label(self, font=('Arial', 14), width=20),
            'style': tk.Label(self, font=('Arial', 12)),
            'language': self.language_display(self),
            'randomwords': self.random_words_display(self)}
        for row, display in enumerate(self.displays.values(), start=1):
            display.grid(row=row, column=0)
        tk.Label(self, height=1000).grid(row=len(self.displays), column=0)

    @property
    def headings(self):
        return self.headings_frame.headings

    @headings.setter
    def headings(self, names):
        self.headings_frame.headings = names
    
    def update(self, displays: Optional[dict[Variable]] = None):
        for name, obj in self.displays.items():
            with ignored(KeyError):
                variable = displays[name]
                obj.config(textvariable=variable)

    def pack(self, *args, **kwargs):
        super().pack(*args, **kwargs)
        return self

    def create_headings(self, parent):
        frame = HeadingFrame(parent, bounds=(1, 10))
        frame.grid(row=0, column=0)
        return frame

    def language_display(self, parent):
        translator = conversion.Translator()
        languages = [f'{code}: {lang().name}'
                     for code, lang in translator.languages.items()]
        menu = ttk.Combobox(parent,
                            values=languages,
                            height=2000,
                            width=25,
                            justify=tk.CENTER)
        menu.state(['readonly'])
        return menu

    def random_words_display(self, parent):
        label = tk.Label(parent, font=('Arial', 14))
        return label
