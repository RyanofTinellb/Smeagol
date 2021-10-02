import tkinter as Tk

from . import options, sample, font, paragraph
from .colour import Colour as ColourFrame


class FullEditor(Tk.Frame):
    def __init__(self, parent, style):
        super().__init__(parent)
        self.parent.title(f'"{style.name.capitalize()}" Style')
        self.backup = style.copy()
        self.style = style
        self.parent.protocol('WM_DELETE_WINDOW', self.cancel)
        for frame, location in self.frames:
            frame(self, self.style).grid(**location)

    @property        
    def parent(self):
        return self.master

    @property
    def frames(self):
        return (
            (font.Frame, dict(row=0, column=0)),
            (paragraph.Frame, dict(row=0, column=1)),
            (ColourFrame, dict(row=1, column=0, columnspan=2)),
            (options.Frame, dict(row=0, column=2)),
            (sample.Frame, dict(row=2, column=0, padx=20, columnspan=3)),
            (self.buttons_frame, dict(row=2, column=2, sticky='se')))

    def buttons_frame(self, *_):
        frame = Tk.Frame(self)
        Tk.Button(frame, text='Cancel', command=self.cancel).grid(
            row=0, column=0)
        Tk.Button(frame, text='OK', command=self.ok).grid(
            row=0, column=1)
        return frame

    def cancel(self):
        self.style = self.backup
        self.parent.destroy()

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
