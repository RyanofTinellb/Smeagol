from tkinter import ttk

from .spinner import Spinner


class Direction(ttk.LabelFrame):
    def __init__(self, parent, style):
        super().__init__(parent, **self.options)
        self.style = style
        for var, row, column in self.spinners:
            Spinner(self, style, var).grid(row=row, column=column)

    @property
    def options(self):
        return dict(
            text='margins and padding',
            padding=10)

    @property
    def spinners(self):
        return (
            (self.style.left, 1, 0),
            (self.style.top, 0, 1),
            (self.style.right, 1, 2),
            (self.style.bottom, 2, 1))
