import tkinter as tk

from smeagol.widgets.heading.heading import Heading


class HeadingFrame(tk.Frame):
    def __init__(self, parent, bounds):
        super().__init__(parent)
        self._commands = []
        self.min, self.max = bounds
        self.min = min(self.min, 1)
        self._headings = []
        self.add_heading()

    @property
    def commands(self):
        return self._commands

    @commands.setter
    def commands(self, commands):
        self._commands = commands
        for heading in self._headings:
            heading.bind_commands(commands)

    @property
    def headings(self):
        return [h.get() for h in self._headings]

    @headings.setter
    def headings(self, names):
        while len(self._headings) > len(names):
            success = self.remove_heading()
            if not success:
                break
        while len(self._headings) < len(names):
            success = self.add_heading()
            if not success:
                break
        for name, heading in zip(names, self._headings):
            heading.set(name)

    def add_heading(self):
        if (i := len(self._headings)) < self.max:
            heading = Heading(i, self)
            heading.bind_commands(self._commands)
            self._headings.append(heading.grid())
            return heading
        return None

    def remove_heading(self):
        if len(self._headings) > self.min:
            heading = self._headings.pop()
            heading.destroy()
            return True
        return False

    def select_last(self):
        self._headings[-1].focus_set()
