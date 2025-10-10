import tkinter as tk
from tkinter import Variable
from typing import Optional


from smeagol.utilities.utils import ignored
from smeagol.widgets.heading.heading_frame import HeadingFrame
from smeagol.widgets.language_selector import LanguageSelector


class Sidebar(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._row = 0
        self.headings_frame = self.create_headings(self)
        self.displays = {
            'wordcount': tk.Label(self, font=('Arial', 14), width=20),
            'style': tk.Label(self, font=('Arial', 12)),
            'language_code': self.create_language_selector(self),
            'randomwords': self.random_words_display(self)}
        for display in self.displays.values():
            display.grid(row=self._row, column=0)
            self._row += 1
        tk.Label(self, height=1000).grid(row=self._row, column=0)

    def go_to_headings(self):
        self.headings_frame.select_last()

    @property
    def title_display(self):
        return self.displays['title']

    @title_display.setter
    def title_display(self, value):
        self.displays.update({'title': value})

    @property
    def language_selector(self):
        return self.displays['language_code']

    @property
    def languages(self):
        return self.language_selector.languages

    @languages.setter
    def languages(self, languages):
        self.language_selector.languages = languages

    @property
    def headings(self):
        return self.headings_frame.headings

    @headings.setter
    def headings(self, names):
        self.headings_frame.headings = names

    def update(self, displays: dict[str, Variable]):
        for name, obj in self.displays.items():
            with ignored(KeyError):
                variable = displays[name]
                obj.config(textvariable=variable)

    def pack(self, *args, **kwargs):
        super().pack(*args, **kwargs)
        return self

    def create_headings(self, parent):
        frame = HeadingFrame(parent, bounds=(1, 10))
        frame.grid(row=self._row, column=0)
        self._row += 1
        return frame

    def create_language_selector(self, parent):
        language_selector = LanguageSelector(parent)
        language_selector.grid(row=self._row, column=0)
        self._row += 1
        return language_selector

    def random_words_display(self, parent):
        label = tk.Label(parent, font=('Arial', 14))
        return label

    def add_heading(self):
        return self.headings_frame.add_heading()
