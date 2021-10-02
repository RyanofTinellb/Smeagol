import json
import os
import random
import re
import time
import tkinter as Tk
from tkinter import filedialog as fd
from tkinter import simpledialog as sd
from tkinter import ttk

from ..utilities import errors
from ..utilities import filesystem as fs
from ..utilities import errors, utils
from ..conversion import api as conversion
from ..widgets import api as wd
from .interface.interfaces import Interfaces

class Editor(Tk.Frame):
    def __init__(self, parent=None, filename=None):
        super().__init__(parent)
        self.parent = self.master
        self.interfaces = Interfaces()
        self.parent.withdraw()
        self.parent.protocol('WM_DELETE_WINDOW', self.quit)
        self.closed_tabs = []
        self.create_layout(self.parent)
        self.new_tab()
        if filename:
            self.open_site(filename)

    def __getattr__(self, attr):
        if attr == 'tab':
            return self.notebook.nametowidget(self.notebook.select())
        if attr == 'textbox':
            return self.tab.textbox
        if attr == 'interface':
            try:
                return self.tab.interface
            except AttributeError:
                return self.interfaces.blank
        if attr == 'entry':
            return self.tab.entry
        try:
            return getattr(super(), attr)
        except AttributeError:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{attr}'")

    def __setattr__(self, attr, value):
        if attr == 'title':
            self.parent.title(f'{value} - Sméagol Site Editor')
        elif attr == 'interface':
            self.tab.interface = value
        elif attr == 'entry':
            self.tab.entry = value
        else:
            super().__setattr__(attr, value)

    @property
    def info(self):
        '''override Tk.Frame.info'''
        return self.textbox.info

    def create_layout(self, parent):
        top = self.winfo_toplevel()
        self.set_window_size(top)
        top['menu'] = self.menu(top, self.menu_commands)
        self.textframe(parent).pack(side=Tk.RIGHT, expand=True, fill=Tk.BOTH)
        self.sidebar(parent).pack(side=Tk.LEFT)

    def set_window_size(self, top):
        top.state('normal')
        w = w_pos = int(top.winfo_screenwidth() / 2)
        h = top.winfo_screenheight() - 50
        h_pos = 0
        top.geometry(f'{w}x{h}+{w_pos}+{h_pos}')

    @staticmethod
    def menu(parent, commands):
        menubar = Tk.Menu(parent)
        for menu in commands:
            submenu = Tk.Menu(menubar, tearoff=0)
            label, options = menu
            menubar.add_cascade(label=label, menu=submenu)
            for option in options:
                label, command = option
                underline = label.find('_')
                underline = 0 if underline == -1 else underline
                label = label.replace('_', '')
                keypress = label[underline]
                submenu.add_command(label=label, command=command,
                                    underline=underline)
                submenu.bind(f'<KeyPress-{keypress}>', command)
        return menubar

    def textframe(self, parent):
        frame = Tk.Frame(parent)
        self.notebook = self.new_notebook(frame)
        self.notebook.pack(side=Tk.TOP, expand=True, fill=Tk.BOTH)
        return frame

    def new_notebook(self, parent):
        notebook = ttk.Notebook(parent)
        notebook.bind('<<NotebookTabChanged>>', self.change_tab)
        notebook.bind('<Button-2>', self.close_tab)
        return notebook

    def sidebar(self, parent):
        frame = Tk.Frame(parent)
        self.headings = self.headings_frame(frame).grid(row=0, column=0)
        self.displays = dict(
            wordcount=Tk.Label(frame, font=('Arial', 14), width=20),
            style=Tk.Label(frame, font=('Arial', 12)),
            language=self.language_display(frame),
            randomwords=self.random_words_display(frame),
            blank=Tk.Label(frame, height=1000))
        for row, display in enumerate(self.displays.values(), start=1):
            display.grid(row=row, column=0)
        return frame

    def headings_frame(self, parent):
        frame = wd.HeadingFrame(parent, bounds=(1, 10))
        frame.commands = self.heading_commands
        return frame

    def update_displays(self):
        for name, display in self.displays.items():
            if name != 'blank':
                display.config(textvariable=self.info[name])

    def random_words_display(self, parent):
        label = Tk.Label(parent, font=('Arial', 14))
        label.bind('<Button-1>', self.refresh_random)
        label.bind('<Button-3>', self.clear_random)
        return label

    def language_display(self, parent):
        translator = conversion.Translator()
        languages = [f'{code}: {lang().name}'
                     for code, lang in translator.languages.items()]
        menu = ttk.Combobox(parent,
                        values=languages,
                        height=2000,
                        width=25,
                        justify=Tk.CENTER)
        menu.state(['readonly'])
        menu.bind('<<ComboboxSelected>>', self.change_language)
        return menu

    def add_commands(self, tkobj, commands):
        for (keys, command) in commands:
            if isinstance(keys, str):
                try:
                    tkobj.bind(keys, command)
                except AttributeError:
                    self.bind_class(tkobj, keys, command)
            else:
                for key in keys:
                    try:
                        tkobj.bind(key, command)
                    except AttributeError:
                        self.bind_class(tkobj, key, command)

    def change_language(self, event=None):
        language = self.info['language'].get()
        self.interface.change_language(language)
        return 'break'

    def go_to(self, position):
        self.textbox.mark_set(Tk.INSERT, position)
        self.textbox.see(Tk.INSERT)

    def new_tab(self, event=None, interface=None):
        interface = interface or self.interface
        wd.Tab(self.notebook, interface)
        self.add_commands(self.textbox, self.textbox_commands)
        return 'break'

    def change_tab(self, event=None):
        self.update_displays()
        self.change_language()
        self.textbox.set_styles()
        self.set_headings(self.entry)
        self.title = self.interface.site.root.name

    def close_tab(self, event=None):
        if self.notebook.index('end') - len(self.closed_tabs) > 1:
            tab = f'@{event.x},{event.y}'
            while True:
                try:
                    self.notebook.hide(tab)
                    self.closed_tabs += [tab]
                    break
                except Tk.TclError:
                    tab = self.notebook.select()
        return 'break'

    def reopen_tab(self, event=None):
        with utils.ignored(IndexError):
            tab = self.closed_tabs.pop()
            self.notebook.add(tab)
            self.notebook.select(tab)
        return 'break'

    def _entry(self, level):
        return self.interface.find_entry(self.headings.headings[:level+1])

    def previous_entry(self, event):
        entry = self._entry(event.widget.level)
        with utils.ignored(IndexError):
            self.set_headings(entry.previous_sister)
        return 'break'

    def next_entry(self, event):
        entry = self._entry(event.widget.level)
        try:
            entry = entry.next_sister
        except IndexError:
            with utils.ignored(IndexError):
                entry = entry.eldest_daughter
        self.set_headings(entry)
        return 'break'

    def load_entry(self, event):
        self.entry = self._entry(event.widget.level)
        try:
            self.set_headings(self.entry.eldest_daughter)
            self.headings.select_last()
        except IndexError:
            self.textbox.focus_set()
            self.textbox.see(Tk.INSERT)

    def open_entry_in_browser(self, event=None):
        self.interface.open_entry_in_browser(self.entry)
        return 'break'

    def open_entry(self, entry):
        self.set_headings(entry)
        self.textbox.set_styles()
        self.entry = entry
        self.title = self.interface.site.root.name

    def reset_entry(self, event=None):
        with utils.ignored(AttributeError):
            self.set_headings(self.entry)

    def open_site(self, filename=''):
        self.interface = self.interfaces[filename]
        for i, entry in enumerate(self.interface.entries):
            if i:
                self.new_tab()
            self.open_entry(entry)

    def save_site(self, filename=''):
        try:
            self.interface.save()
        except IOError:
            self.save_site_as()

    def save_site_as(self, filename=''):
        filename = filename or fs.save_smeagol()
        if filename:
            self.interface.filename = filename
            self.save_site()

    def set_headings(self, entry):
        self.headings.headings = [e.name for e in entry.lineage][1:]

    def rename_page(self, event=None):
        name = self.entry.name
        name = sd.askstring(
            'Page Name', f'What is the new name of "{name}"?')
        if name:
            self.entry.name = name
            self.tab.name = name
            self.reset_entry()
    
    def save_page(self, event=None):
        self.interface.save_page(self.textbox.formatted_text, self.entry)
        self.interface.save_site()
        return 'break'

    def refresh_random(self, event=None):
        if r := self.interface.randomwords:
            self.info['randomwords'].set('\n'.join(r.words))
        return 'break'

    def clear_random(self, event=None):
        self.info['randomwords'].set('')
        return 'break'

    def replace(self, heading, text):
        heading.delete(*Tk.ALL)
        heading.insert(Tk.FIRST, text)

    def display(self, text):
        self.textbox.replace(str(text))
        self.textbox.focus_set()
        self.update_wordcount(self.textbox)
        self.hide_tags()

    def select_word(self, event):
        textbox = event.widget
        pattern = r'\n|[^a-zA-Z0-9_\'’-]'
        borders = (
            textbox.search(
                pattern, Tk.INSERT, backwards=True, regexp=True
            ) + '+1c' or Tk.INSERT + ' linestart',
            textbox.search(
                pattern, Tk.INSERT, regexp=True
            ) or Tk.INSERT + ' lineend'
        )
        textbox.tag_add(Tk.SEL, *borders)
        return textbox.get(*borders)

    def markdown_clear(self, event=None):
        text = self.interface.markdown.to_markup(self.textbox.text)
        self.textbox.replace(text)

    def markdown_apply(self, event=None):
        text = self.interface.markdown.to_markdown(self.textbox.text)
        self.textbox.replace(text)

    def markdown_edit(self, event=None):
        top = Tk.Toplevel(self)
        editor = window.MarkdownWindow(top, self.interface.markdown)
        self.wait_window(top)
        self.interface.markdown = editor.markdown
    
    def template_edit(self, event=None):
        top = Tk.Toplevel(self)
        templates = self.interface.templates
        window.Templates(top, self.interface.templates).grid()
        self.wait_window(top)
        for template in templates.values():
            if template.edited:
                template.edited = False
                self.new_tab(interface=template)

    def edit_styles(self, event=None):
        top = Tk.Toplevel()
        window = wd.styles.Window(top, self.interface.styles)
        window.grid()
        top.protocol('WM_DELETE_WINDOW', window.cancel)
        top.title(f'{self.interface.site.name} Styles')
        self.wait_window(top)
        self.textbox.update_styles()
        self.interface.config['styles'] = dict(self.interface.styles.items())

    def show_window(self):
        self.set_window_size(self.top)
        self.parent.update()
        self.parent.deiconify()

    def quit(self):
        for interface in self.interfaces.values():
            with utils.utils.ignored(IOError):
                interface.save()
        self.parent.withdraw()
        self.parent.quit()
        print('Closing Servers...')
        fs.close_servers()
        print('Servers closed. Enjoy the rest of your day.')

    @property
    def menu_commands(self):
        return [
            ('Site', [
                ('Open', self.open_site),
                ('Save', self.save_site),
                ('Save _As', self.save_site_as)]),
            ('Page', [
                ('Rename', self.rename_page),
                ('Open in Browser', self.open_entry_in_browser)
            ]),
            ('Edit', [
                ('Styles', self.edit_styles),
                ('Markdown', self.markdown_edit),
                ('Templates', self.template_edit)])]

    @property
    def textbox_commands(self):
        return [('<Control-r>', self.refresh_random),
                ('<Control-s>', self.save_page),
                ('<Control-t>', self.new_tab),
                ('<Control-T>', self.reopen_tab),
                ('<Control-w>', self.close_tab),
                ('<Enter>', self.reset_entry)]

    @property
    def heading_commands(self):
        return [('<Prior>', self.previous_entry),
                ('<Next>', self.next_entry),
                ('<Return>', self.load_entry)]
