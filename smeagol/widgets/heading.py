from itertools import zip_longest
import tkinter as Tk


class HeadingFrame(Tk.Frame):
    def __init__(self, parent, bounds):
        super().__init__(parent)
        self.min, self.max = bounds
        self._headings = []

    @property
    def headings(self):
        return [h.get() for h in self._headings]

    @headings.setter
    def headings(self, entries):
        entries = [x for x in zip_longest(entries, self._headings)]
        for entry, heading in entries:
            if heading is None:
                self.add_heading(entry)
            elif entry is None:
                success = self.remove_heading(heading)
                if not success:
                    heading.set()
            else:
                heading.set(entry)

    def grid(self, *args, **kwargs):
        super().grid(*args, **kwargs)
        return self

    def add_heading(self, entry=None):
        if (i := len(self._headings)) < self.max:
            heading = Heading(i, self)
            heading.bind_commands(self.commands)
            self._headings.append(heading.grid())
            if entry is not None:
                heading.set(entry)
            return True

    def remove_heading(self, heading):
        if len(self._headings) > self.min:
            heading.destroy()
            self._headings.remove(heading)
            return True
        
    def select_last(self):
        self._headings[-1].focus_set()
        
    @property
    def commands(self):
        return self._commands

    @commands.setter
    def commands(self, commands):
        self._commands = commands
        for heading in self._headings:
            heading.bind_commands(self.commands)


class Heading(Tk.Entry):
    def __init__(self, level, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.level = level

    def bind_commands(self, commands):
        for key, command in commands:
            self.bind(f'{key}', command)

    def set(self, value=''):
        self.delete(0, 'end')
        self.insert(0, value)

    def grid(self, *args, **kwargs):
        super().grid(*args, **kwargs)
        return self
