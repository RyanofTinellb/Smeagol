import tkinter as tk
from tkinter import colorchooser as ColourChooser
from tkinter import ttk


class Colour(ttk.LabelFrame):
    def __init__(self, parent, style):
        super().__init__(parent, text='colour')
        self.style = style
        for col, (attr, var) in enumerate(self.selectors):
            self.Label(attr).grid(row=0, column=2*col)
            self.Button(attr, var).grid(row=0, column=2*col+1)

    def Label(self, attr):
        return ttk.Label(self, text=attr, padding=(15, 0, 5, 0))

    def Button(self, attr, var):
        button = tk.Button(self, background=var.get(), width=2)
        button.config(command=lambda *_: self.change_colour(button, attr, var))
        return button

    def change_colour(self, button, attr, var):
        colour = self.choose_colour(attr, var)
        if colour:
            var.set(colour)
            button.config(background=colour)

    def choose_colour(self, attr, var):
        options = dict(
            color=var.get(),
            title=f'{attr.capitalize()} Colour')
        _, colour = ColourChooser.askcolor(**options)
        return colour

    @property
    def selectors(self):
        return (
            ('text', self.style.colour),
            ('background', self.style.background))
