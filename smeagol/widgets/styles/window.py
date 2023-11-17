import tkinter as tk
import tkinter.messagebox as mb
import tkinter.simpledialog as sd
import tkinter.ttk as ttk

from .editor import DefaultEditor, FullEditor
from .interface import Interface


class Window(tk.Frame):
    def __init__(self, parent=None, styles=None):
        super().__init__(parent)
        self.styles = styles
        self.original = styles.copy()
        self.styles_box(self).grid(
            row=0, column=0, columnspan=3, sticky='s', padx=10, pady=5)
        self.style_buttons(self).grid(row=1, column=0, padx=10)
        self.sample_box(self).grid(row=0, column=4, rowspan=3,
                                   columnspan=2, padx=10, pady=5)
        self.window_buttons(self).grid(row=4, column=5, padx=10, sticky='e')
        self.select_style()
    
    @property
    def parent(self):
        return self.master

    def style_buttons(self, parent=None):
        frame = tk.Frame(parent)
        tk.Button(frame, text='Edit', command=self.edit).grid(row=0, column=0)
        self.rename_btn = tk.Button(frame, text='Rename', command=self.rename)
        self.rename_btn.grid(row=0, column=1)
        self.delete_btn = tk.Button(frame, text='Delete', command=self.delete)
        self.delete_btn.grid(row=0, column=2, sticky='w')
        tk.Button(frame, text='New', command=self.add).grid(row=0, column=3)
        return frame

    def styles_box(self, parent=None):
        box = ttk.Combobox(parent, values=self.styles.names)
        box.bind('<<ComboboxSelected>>', self.select_style)
        box.set('default')
        self.current = box
        return box

    def select_style(self, event=None):
        style = self.styles[self.current.get()]
        state = 'disabled' if style.name == 'default' else 'normal'
        self.delete_btn.config(state=state)
        self.rename_btn.config(state=state)
        font = style.Font
        self._sample.tag_delete('sample')
        self._sample.tag_add('sample', 1.0, 'end')
        self._sample.tag_config('sample', font=font, **style.paragraph)

    def window_buttons(self, parent=None):
        frame = tk.Frame(parent)
        button = tk.Button(frame, text='Cancel', command=self.cancel)
        button.grid(row=0, column=0)
        button = tk.Button(frame, text='OK', command=self.ok)
        button.grid(row=0, column=1)
        return frame

    def sample_box(self, parent=None):
        box = tk.Text(parent, height=3, width=20)
        box.insert(tk.INSERT, 'Sample', 'sample')
        box.config(state='disabled')
        self._sample = box
        return box

    def rename(self, event=None):
        style = self.current.get()
        name = sd.askstring(
            'Style Name', f'What is the new name of "{style}"?')
        if name and name not in self.styles:
            self.styles[style].name = name
            self.styles[name] = self.styles[style]
            self.styles.remove(style)
            self.current.config(values=self.styles.names)
            self.current.set(name)
            self.select_style()

    def edit(self, event=None):
        top = tk.Toplevel()
        editor = self._editor(top, style=Interface(self.style))
        editor.grid()
        self.parent.withdraw()
        self.wait_window(top)
        self.styles[self.current.get()] = editor.style
        self.select_style()
        self.parent.deiconify()
    
    @property
    def style(self):
        return self.styles[self.current.get()]
    
    @property
    def style_name(self):
        return self.current.get()
    
    @style_name.setter
    def style_name(self, value):
        self.current.set(value)
    
    @property
    def _editor(self):
        return DefaultEditor if self.style.name == 'default' else FullEditor

    def add(self, event=None):
        name = sd.askstring('Style Name', 'What is the name of the new style?')
        if name and name not in self.styles:
            self.styles.add(name)
            self.current.config(values=self.styles.names)
            self.current.set(name)
            self.select_style()
            self.edit()

    def delete(self, event=None):
        message = f'Are you sure you wish to delete the style "{self.style_name}"?'
        if mb.askyesno('Delete', message):
            self.styles.remove(self.style_name)
            self.current.config(values=self.styles.names)
            self.style_name = 'default'
            self.select_style()

    def cancel(self):
        self.parent.destroy()

    def ok(self):
        self.original.update(self.styles)
        self.cancel()
