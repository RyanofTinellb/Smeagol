import tkinter as tk
from itertools import zip_longest

from smeagol.widgets.heading.heading import Heading


class HeadingFrame(tk.Frame):
    def __init__(self, parent, bounds):
        super().__init__(parent)
        self.min, self.max = bounds
        self.min = min(self.min, 1)
        self._headings = []
        self.add_heading()

    @property
    def headings(self):
        return [h.get() for h in self._headings]

    @headings.setter
    def headings(self, names):
        self.add_heading()
        for name, heading in zip_longest(names, self._headings):
            if heading is None:
                self.add_heading(name)
            elif name is None:
                success = self.remove_heading(heading)
                if not success:
                    heading.set()
            else:
                heading.set(name)

    def add_heading(self, entry=None):
        if (i := len(self._headings)) < self.max:
            heading = Heading(i, self)
            heading.bind_commands(self.commands)
            self._headings.append(heading.grid())
            if entry is not None:
                heading.set(entry)
            return True
        return False

    def remove_heading(self, heading):
        if len(self._headings) > self.min:
            heading.destroy()
            self._headings.remove(heading)
            return True
        return False

    def select_last(self):
        self._headings[-1].focus_set()

    @property
    def commands(self):
        return self._commands

    @property
    def _commands(self):
        return []
        #     ('<Prior>', self.previous_entry),
        #     ('<Next>', self.next_entry),
        #     ('<Return>', self.load_entry),
        # ]
