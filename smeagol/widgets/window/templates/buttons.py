import tkinter as tk


class Buttons(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        new = tk.Button(self, text='New', command=parent.new)
        new.grid(row=0, column=0, sticky='e')
        add = tk.Button(self, text='Open', command=parent.add)
        add.grid(row=0, column=1)
        cancel = tk.Button(self, text='Cancel', command=parent.cancel)
        cancel.grid(row=0, column=2, sticky='ew')
        done = tk.Button(self, text='OK', command=parent.done)
        done.grid(row=0, column=3, sticky='w')
