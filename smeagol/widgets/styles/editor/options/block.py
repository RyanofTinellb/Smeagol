import tkinter as tk


class Block(tk.Frame):
    def __init__(self, parent, style):
        super().__init__(parent)
        self.style = style
        tk.Label(self, text='block').grid(row=0, column=0)
        self.Box.grid(row=0, column=1)

    @property
    def Box(self):
        return tk.Entry(self, **self.box_options)

    @property
    def box_options(self):
        return dict(
            width=30,
            textvariable=self.style.block)