import re
import tkinter as Tk
from tkinter import ttk
from tkinter.font import Font

from smeagol.utils import ignored

from . import options, sample, font
from .colour import Colour as ColourFrame


class FullEditor(Tk.Frame):
    def __init__(self, parent, style):
        super().__init__(parent)
        self.grid()
        parent.title(style.name)
        self.backup = style.copy()
        self.style = style
        self.spinners = []
        self.non_spinners = []
        for frame, options in self.frames:
            frame(self, self.style).grid(**options)

    @property        
    def parent(self):
        return self.master

    @property
    def frames(self):
        return (
            (font.Frame, dict(row=0, column=0)),
            (ColourFrame, dict(row=1, column=0)),
            (sample.Frame, dict(row=2, column=0, padx=20)),
            (self.buttons_frame, dict(row=2, column=1, sticky='s')))

    def buttons_frame(self, *_):
        frame = Tk.Frame(self)
        Tk.Button(frame, text='Cancel', command=self.cancel).grid(
            row=0, column=0)
        Tk.Button(frame, text='OK', command=self.ok).grid(
            row=0, column=1)
        return frame

    def cancel(self):
        self.style = self.backup
        self.ok()

    def ok(self):
        self.style = self.style.style
        self.parent.destroy()

    def enable_para_elements(self):
        for _, elt in self.spinners:
            elt.config(state='normal')
        for _, elt in self.non_spinners:
            elt.config(state='readonly')

    def disable_para_elements(self):
        for _, elt in self.spinners + self.non_spinners:
            elt.config(state='disabled')

    def set_para_element_state(self, event=None):
        if self.block_box.get():
            self.enable_para_elements()
        else:
            self.disable_para_elements()
