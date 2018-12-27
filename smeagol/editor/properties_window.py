import Tkinter as Tk
import tkFileDialog as fd
from properties import Properties
from smeagol.utils import *
from smeagol.defaults import default

class PropertiesWindow(Tk.Toplevel, object):
    def __init__(self, properties=None, master=None):
        super(PropertiesWindow, self).__init__(master)
        self.properties = properties or Properties()
        properties = json.loads(default.properties)
        self.property_frames = []
        for row, property in enumerate(properties):
            self.prepare(property, row)
            frame = PropertyFrame(property, master=self)
            self.property_frames.append(frame)
        self.configure_buttons(row+1)
        self.property_frames[0].entry.focus_set()

    def __getattr__(self, attr):
        return getattr(self.properties, attr)

    def prepare(self, properties, row):
        properties['row'] = row
        owner = properties['owner']
        property = properties['property']
        if owner == 'links':
            properties['value'] = self.links.get(property, '')
            properties['checked'] = property in self.links
        else:
            properties['value'] = getattr(self, property)

    def configure_buttons(self, row):
        done = Tk.Button(self, text='OK', command=self.done)
        done.grid(row=row, column=3, sticky=Tk.E+Tk.W)
        cancel = Tk.Button(self, text='Cancel', command=self.cancel)
        cancel.grid(row=row, column=2, sticky=Tk.E)

    def done(self, event=None):
        for frame in self.property_frames:
            value = frame.get()
            self.properties.update(value)
        self.destroy()

    def cancel(self, event=None):
        self.destroy()

class PropertyFrame(object):
    def __init__(self, property, master):
        self.property = property
        self.master = master
        self.ready_label()
        if self.check:
            self.ready_checkbox()
        if self.textbox:
            self.ready_entry()
        if self.browse:
            self.ready_browser()
            self.ready_button()

    def __getattr__(self, attr):
        if attr in {'name', 'owner', 'textbox', 'browse',
                        'value', 'checked', 'row'}:
            return self.property[attr]
        else:
            return getattr(super(PropertyFrame, self), attr)

    def __setattr__(self, attr, value):
        if attr in {'value', 'checked'}:
            self.property[attr] = value
        else:
            super(PropertyFrame, self).__setattr__(attr, value)

    @property
    def check(self):
        return self.owner == 'links'

    def ready_checkbox(self):
        self.checkvar = Tk.IntVar()
        self.checkvar.set(self.checked)
        check = Tk.Checkbutton(self.master, variable=self.checkvar)
        check.grid(row=self.row, column=0)

    def ready_label(self):
        label = Tk.Label(self.master, text=self.name)
        label.grid(row=self.row, column=1, sticky=Tk.W)

    def ready_entry(self):
        self.entryvar = Tk.StringVar()
        self.entryvar.set(self.value)
        self.entry = Tk.Entry(self.master, width=50, textvariable=self.entryvar)
        self.entry.bind('<Return>', self.master.done)
        self.entry.bind('<Escape>', self.master.cancel)
        self.entry.grid(row=self.row, column=2)
        self.entry.xview('end')

    def ready_button(self):
        button = Tk.Button(self.master,
                           text='Browse...',
                           command=self.browse)
        button.grid(row=self.row, column=3)

    def ready_browser(self):
        if self.browse == 'folder':
            self.browse = self.browse_folder
        else:
            self.browse = self.file_browser()

    def browse_folder(self):
        filename = fd.askdirectory()
        self.insert(filename)
        self.entry.focus_set()

    def file_browser(self):
        browse = self.browse
        filetype = (browse['text'], browse['extension'])
        def browse_file():
            action = browse['action']
            if action == 'open':
                browser = fd.askopenfilename
            elif action == 'save':
                browser = fd.asksaveasfilename
            filename = browser(filetypes=[filetype], title='Select File')
            extension = filetype[1]
            self.insert(filename)
            if filename:
                if action == 'save':
                    with open(filename, 'a') as textfile:
                        textfile.write
                with ignored(AttributeError):
                    self.check.select()
            self.entry.focus_set()
        return browse_file

    def insert(self, text=''):
        if text:
            self.entryvar.set(text)
        self.entry.xview('end')

    def get(self):
        if self.textbox:
            self.value = self.entryvar.get()
        if self.check:
            self.checked = self.checkvar.get()
        return self.property