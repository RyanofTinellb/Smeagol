import os.path
from smeagol import utils
import tkinter as Tk
from tkinter import simpledialog as sd
from .row import Row
from .buttons import Buttons

class Templates(Tk.Frame):
    '''Templates Window'''
    def __init__(self, parent, templates=None, editor=None):
        '''
        @param editor: function to edit template from Editor or derived class
            thereof
        '''
        super().__init__(parent)
        self.parent.protocol('WM_DELETE_WINDOW', self.cancel)
        self.parent.title('Templates')
        self.templates = templates or {}
        self.frames = []
        self.main_frame = self._main_frame
        for row, (name, template) in enumerate(templates.items()):
            if name:
                self.frames.append(self._new(name, template, row))
        buttons = Buttons(parent=self)
        buttons.grid(row=row+1, column=0, sticky=Tk.E)
        self.frames[0].entry.focus_set()
    
    @property
    def _main_frame(self):
        frame = Tk.Frame(self)
        frame.parent = frame.master
        frame.grid()
        return frame
    
    @property
    def parent(self):
        return self.master

    def done(self, event=None):
        self.templates = [frame.get() for frame in self.frames]
        self.parent.destroy()
        return 'break'

    def cancel(self, event=None):
        self.templates = []
        self.parent.destroy()
        return 'break'
    
    def get(self):
        return self.templates

    def append(self):
        template = self.templates[None].copy()
        name = self._ask_name
        self.frames.append(frame := self._new(name, template))
        return frame

    def _ask_name(self):
        return sd.askstring(
            'Template Name',
            'What is the new name of the new template?')

    def _new(self, name, template, row=None):
        row = len(self.frames) if row is None else row
        return Row(self.main_frame, name, template, self, row=row)

    def new(self, event=None):
        self.append().save().edit()

    def add(self, event=None):
        self.append().open()
    
    def remove(self, frame):
        self.frames.remove(frame)