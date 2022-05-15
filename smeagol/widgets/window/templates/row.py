import os
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import simpledialog as sd


class Row:
    def __init__(self, parent, name, template, window, row):
        self.parent = parent
        self.name = name
        self.template = template
        self.window = window
        self.row = row
        self.widgets = []
        self.ready_label()
        self.ready_entry()
        self.ready_buttons()

    def ready_label(self):
        self.labelvar = tk.StringVar()
        self.labelvar.set(self.name)
        label = tk.Label(self.parent, text=self.name,  # width=20,
                         textvariable=self.labelvar)
        label.grid(row=self.row, column=1, sticky='ew')
        self.widgets += [label]

    def ready_entry(self):
        self.entryvar = tk.StringVar()
        self.entryvar.set(self.template.filename)
        entry = tk.Entry(self.parent, textvariable=self.entryvar, width=50)
        entry.bind('<Return>', self.window.done)
        entry.bind('<Escape>', self.window.cancel)
        entry.grid(row=self.row, column=2)
        entry.xview(tk.LAST)
        entry.icursor(tk.LAST)
        self.entry = entry
        self.widgets += [entry]

    def ready_buttons(self):
        state = tk.NORMAL if self.template.optional else tk.DISABLED

        buttons = (('0', 'Rename', self.change_name),
                   ('6', 'Remove', self.remove))
        for button in buttons:
            column, text, command = button
            new = tk.Button(self.parent,
                            text=text,
                            command=command,
                            state=state)
            new.grid(row=self.row, column=column)
            self.widgets += [new]

        buttons = (('5', 'Edit', self.edit),
                   ('3', 'Open', self.open),
                   ('4', 'New', self.save))
        for button in buttons:
            column, text, command = button
            new = tk.Button(self.parent,
                            text=text,
                            command=command)
            new.grid(row=self.row, column=column)
            self.widgets += [new]

    def edit(self):
        self.get()
        self.parent.parent.parent.destroy()

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
                            initialvalue=self.name)
        self.labelvar.set(name or self.labelvar.get())

    def insert(self, text=''):
        if text:
            self.entryvar.set(text)
        self.entry.xview('end')

    def get(self):
        self.name = self.labelvar.get()
        self.template.filename = self.entryvar.get()