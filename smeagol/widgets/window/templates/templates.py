import tkinter as tk
from tkinter import simpledialog as sd
from .row import Row
from .buttons import Buttons

class Templates(tk.Frame):
    '''Templates Window'''
    def __init__(self, parent, templates):
        '''
        @param editor: function to edit template from Editor or derived class
            thereof
        '''
        super().__init__(parent)
        self.parent.protocol('WM_DELETE_WINDOW', self.cancel)
        self.parent.title('Templates')
        self.templates = templates
        self.copy = templates.copy()
        self.frames = []
        self.main_frame = self._main_frame
        self.main_frame.grid()
        row = self.create_rows(templates)
        buttons = Buttons(parent=self)
        buttons.grid(row=row+1, column=0, sticky=tk.E)
        self.frames[0].entry.focus_set()
        self.return_value = None
    
    def create_rows(self, items, row=0, optional=False):
        for name, item in items:
            if isinstance(item, str):
                row = self.append(name, item, row, optional)
            else:
                row = self.create_rows(item.items(), row, optional=True)
        return row

    def append(self, name, filename, row, optional=False):
        self.frames.append(self._new(name, filename, row, optional))
        return row + 1
    
    def _new(self, name, filename, row, optional=True):
        return Row(self.main_frame, name, filename, optional, self, row=row)
    
    @property
    def _main_frame(self):
        frame = tk.Frame(self)
        frame.parent = frame.master
        return frame
    
    @property
    def parent(self):
        return self.master

    def done(self, event=None):
        for frame in self.frames:
            frame.get()
            print(frame.name, frame.filename)
            setattr(self.templates, frame.name, frame.filename)
        self.parent.destroy()
        return 'break'

    def cancel(self, event=None):
        self.templates.update(self.copy)
        self.parent.destroy()
        return 'break'
    
    def get(self):
        return self.templates

    def add_row(self):
        template = self.templates[None].copy()
        name = self._ask_name
        self.frames.append(frame := self._new(name, template))
        return frame

    def _ask_name(self):
        return sd.askstring(
            'Template Name',
            'What is the new name of the new template?')

    def new(self, event=None):
        self.append().save().edit()

    def add(self, event=None):
        self.append().open()
    
    def remove(self, frame):
        self.frames.remove(frame)