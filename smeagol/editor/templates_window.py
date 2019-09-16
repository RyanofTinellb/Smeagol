import os.path
from ..utils import *

class TemplatesWindow(Tk.Toplevel):
    def __init__(self, templates=None, editor=None, master=None):
        '''
        @param editor: function to edit template from Editor or derived class
            thereof
        '''
        super().__init__(master)
        self.protocol('WM_DELETE_WINDOW', self.cancel)
        self.title('Templates')
        self.templates = templates or []
        self.frames = []
        self.editor = editor
        self.main_frame = Tk.Frame(self)
        for row, template in enumerate(templates):
            frame = TemplateFrame(self.main_frame, template, self, editor, row)
            self.frames.append(frame)
        self.main_frame.grid()
        buttonsframe = ButtonsFrame(master=self)
        buttonsframe.grid(row=row+1, column=0, sticky=Tk.E)
        self.frames[0].entry.focus_set()

    def done(self, event=None):
        self.templates = [frame.get() for frame in self.frames]
        self.destroy()
        return 'break'

    def cancel(self, event=None):
        self.templates = []
        self.destroy()
        return 'break'
    
    def get(self):
        return self.templates

    def append(self):
        template = dict(use_name='', filename='', enabled='True')
        row = len(self.frames)
        frame = TemplateFrame(self.main_frame, template, self,
            self.editor, row=row)
        self.frames.append(frame)
        return frame

    def new(self, event=None):
        self.append().save().edit()

    def add(self, event=None):
        self.append().open()
    
    def remove(self, frame):
        self.frames.remove(frame)


class TemplateFrame():
    def __init__(self, master, template, window, editor, row):
        self.master = master
        self.template = template
        self.window = window
        self.editor = editor
        self.row = row
        self.widgets = []
        self.ready_label()
        self.ready_entry()
        self.ready_buttons()

    def __getattr__(self, attr):
        if attr in {'use_name', 'filename', 'enabled'}:
            return self.template.get(attr, None)
        else:
            return getattr(super(), attr)

    def __setattr__(self, attr, value):
        if attr in {'use_name', 'filename'}:
            self.template[attr] = value
        else:
            super().__setattr__(attr, value)

    def ready_label(self):
        self.labelvar = Tk.StringVar()
        self.labelvar.set(self.use_name)
        label = Tk.Label(self.master, text=self.use_name, # width=20,
                         textvariable=self.labelvar)
        label.grid(row=self.row, column=1, sticky=Tk.W+Tk.E)
        self.widgets += [label]

    def ready_entry(self):
        state = Tk.NORMAL if self.enabled else Tk.DISABLED
        self.entryvar = Tk.StringVar()
        self.entryvar.set(self.filename)
        entry = Tk.Entry(self.master, textvariable=self.entryvar,
            state=state, width=50)
        entry.bind('<Return>', self.window.done)
        entry.bind('<Escape>', self.window.cancel)
        entry.grid(row=self.row, column=2)
        entry.xview(Tk.FINAL)
        entry.icursor(Tk.FINAL)
        self.entry = entry
        self.widgets += [entry]

    def ready_buttons(self):
        state = Tk.NORMAL if self.enabled else Tk.DISABLED

        buttons = (('0', 'Rename', self.change_name),
                   ('6', 'Remove', self.remove))
        for button in buttons:
            new = Tk.Button(self.master,
                            text=button[1],
                            command=button[2],
                            state=state)
            new.grid(row=self.row, column=button[0])
            self.widgets += [new]

        buttons = (('5', 'Edit', self.edit),
                   ('3', 'Open', self.open),
                   ('4', 'New', self.save))
        for button in buttons:
            new = Tk.Button(self.master,
                            text=button[1],
                            command=button[2])
            new.grid(row=self.row, column=button[0])
            self.widgets += [new]
        
    def edit(self):
        self.get()
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                text = file.read()
        except FileNotFoundError:
            text = 'Write a new Template here!'
        text = self.editor(text)
        if text:
            with open(self.filename, 'w', encoding='utf-8') as file:
                file.write(text)
        self.entry.focus_set()

    def remove(self):
        for widget in self.widgets:
            widget.destroy()
        self.window.remove(self)

    def browse_file(self, state):
        dialog = fd.askopenfilename if state == 'open' else fd.asksaveasfilename
        filetype = ('Template', '*.html')  
        filename = dialog(filetypes=[filetype],
                                          title='Select File',
                                          defaultextension=filetype[1][1:])
        self.insert(filename)
        self.entry.focus_set()
        name = os.path.basename(filename).replace('.html', '')
        self.labelvar.set(self.labelvar.get() or os.path.basename(name))

    def open(self):
        self.browse_file('open')
        return self
    
    def save(self):
        self.browse_file('save')
        return self

    def change_name(self):
        name = sd.askstring('Rename Template Reference', 'What is the new name?',
                     initialvalue=self.use_name)
        self.labelvar.set(name or self.labelvar.get())

    def insert(self, text='', multiple=False):
        if text:
            self.entryvar.set(text)
        self.entry.xview('end')

    def get(self):
        self.use_name = self.labelvar.get()
        self.filename = self.entryvar.get()
        return self.template

class ButtonsFrame(Tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        new = Tk.Button(self, text ='New', command=master.new)
        new.grid(row=0, column=0, sticky=Tk.E)
        add = Tk.Button(self, text='Open', command=master.add)
        add.grid(row=0, column=1)
        cancel = Tk.Button(self, text='Cancel', command=master.cancel)
        cancel.grid(row=0, column=2, sticky=Tk.E+Tk.W)
        done = Tk.Button(self, text='OK', command=master.done)
        done.grid(row=0, column=3, sticky=Tk.W)
