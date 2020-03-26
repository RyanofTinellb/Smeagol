import json
import os
import random
import re
import time
import tkinter as Tk
import tkinter.filedialog as fd
import tkinter.ttk as ttk
import webbrowser as web
from tkinter.ttk import Combobox

from .. import conversion, utils
from .. import widgets as wd
from ..utilities import RandomWords
from ..utils import ignored, tkinter
from . import file_system as fs
from .interface import Interface


class Editor(Tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.interfaces = {}
        self.master.withdraw()
        self.master.protocol('WM_DELETE_WINDOW', self.quit)
        self.closed_tabs = []
        self.create_layout(self.master)
        self.new_tab()
        self.open_random_site('c:/users/ryan/tinellbianlanguages')

    def open_random_site(self, root):
        files = [os.path.join(root, file_) for root, _, files in os.walk(root)
                 for file_ in files if file_.endswith('.smg')]
        print(choice := random.choice(files))
        self.open_site(choice)

    def Text(self, text):
        return utils.Text(self, text)

    def __getattr__(self, attr):
        if attr == 'tab':
            return self.notebook.nametowidget(self.notebook.select())
        if attr == 'textbox':
            return self.tab.textbox
        if attr == 'interface':
            return self.textbox.interface
        try:
            return getattr(super(), attr)
        except AttributeError:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{attr}'")

    def __setattr__(self, attr, value):
        if attr == 'title':
            self.master.title(f'{value} - Sméagol Site Editor')
        elif attr == 'interface':
            self.textbox.interface = value
        else:
            super().__setattr__(attr, value)

    @property
    def info(self):
        '''override Tk.Frame.info'''
        return self.textbox.info

    def create_layout(self, master):
        top = self.winfo_toplevel()
        self.set_window_size(top)
        top['menu'] = self.menu(top, self.menu_commands)
        self.textframe(master).pack(side=Tk.RIGHT, expand=True, fill=Tk.BOTH)
        self.sidebar(master).pack(side=Tk.LEFT)

    def set_window_size(self, top):
        top.state('normal')
        w = w_pos = int(top.winfo_screenwidth() / 2)
        h = top.winfo_screenheight() - 50
        h_pos = 0
        top.geometry(f'{w}x{h}+{w_pos}+{h_pos}')

    @staticmethod
    def menu(master, commands):
        menubar = Tk.Menu(master)
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

    def textframe(self, master):
        frame = Tk.Frame(master)
        self.notebook = self.new_notebook(frame)
        self.notebook.pack(side=Tk.TOP, expand=True, fill=Tk.BOTH)
        return frame

    def new_notebook(self, master):
        notebook = ttk.Notebook(master)
        notebook.bind('<<NotebookTabChanged>>', self.change_tab)
        notebook.bind('<Button-2>', self.close_tab)
        return notebook

    def sidebar(self, master):
        frame = Tk.Frame(master)
        self.headings = self.headings_frame(frame).grid(row=0, column=0)
        self.displays = dict(
            wordcount=Tk.Label(master=frame, font=('Arial', 14), width=20),
            style=Tk.Label(master=frame, font=('Arial', 12)),
            language=self.language_display(frame),
            randomwords=self.random_words_display(frame),
            blank=Tk.Label(master=frame, height=1000))
        for row, display in enumerate(self.displays.values(), start=1):
            display.grid(row=row, column=0)
        return frame

    def headings_frame(self, master):
        frame = wd.HeadingFrame(bounds=(1, 10), master=master)
        frame.commands = self.heading_commands
        return frame

    def update_displays(self):
        for name, display in self.displays.items():
            if name != 'blank':
                display.config(textvariable=self.info[name])

    def random_words_display(self, master=None):
        label = Tk.Label(master=master, font=('Arial', 14))
        label.bind('<Button-1>', self.refresh_random)
        label.bind('<Button-3>', self.clear_random)
        return label

    def language_display(self, master):
        translator = conversion.Translator()
        languages = [f'{code}: {lang().name}'
                     for code, lang in translator.languages.items()]
        menu = Combobox(master,
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

    def new_textbox(self, master, interface=None):
        textbox = wd.Textbox(master, interface)
        self.add_commands(textbox, self.textbox_commands())
        return textbox

    def new_tab(self, name='', text='', interface=None):
        notebook = self.notebook
        frame = Tk.Frame(notebook)
        textbox = self.new_textbox(frame, interface)
        textbox.pack(side=Tk.LEFT, expand=True, fill=Tk.BOTH)
        textbox.insert(text)
        frame.textbox = textbox
        notebook.add(frame)
        notebook.select(frame)
        self.rename_tab(name)

    def open_new_tab(self, event=None):
        self.new_tab(interface=self.textbox.interface)

    def change_tab(self, event=None):
        self.update_displays()
        self.change_language()

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
        with ignored(IndexError):
            tab = self.closed_tabs.pop()
            self.notebook.add(tab)
            self.notebook.select(tab)
        return 'break'

    def rename_tab(self, text):
        self.notebook.tab(self.tab, text=text)

    def _entry(self, level):
        return self.interface.find_entry(self.headings.headings[:level+1])

    def previous_entry(self, event):
        with ignored(IndexError):
            self.set_headings(self._entry(event.widget.level).previous_sister)
        return 'break'

    def next_entry(self, event):
        with ignored(IndexError):
            self.set_headings(self._entry(event.widget.level).next_sister)
        return 'break'

    def load_entry(self, event):
        entry = self._entry(event.widget.level)
        self.display_entry(entry)
        try:
            self.set_headings(entry.eldest_daughter)
            self.headings.select_last()
        except IndexError:
            self.textbox.focus_set()
            self.textbox.see(Tk.INSERT)

    def display_entry(self, entry):
        self.textbox.entry = entry
        self.rename_tab(entry.name)

    def open_entry(self, entry):
        self.set_headings(entry)
        self.textbox.set_styles()
        self.display_entry(entry)
        self.title = entry.root.name

    def reset_entry(self, event):
        with ignored(AttributeError):
            self.set_headings(self.textbox.entry)

    def open_site(self, filename=''):
        filename = filename or fs.open_smeagol()
        try:
            self.interface = self.interfaces[filename]
        except KeyError:
            self.interface = self.interfaces[filename] = Interface(filename)
        self.open_entry(self.interface.entry)

    def save_site(self, filename=''):
        self.interface.save_site(filename)

    def save_site_as(self, filename=''):
        self.interface.save_site_as

    def set_headings(self, entry):
        self.headings.headings = [x.name for x in entry.lineage][1:]

    def refresh_random(self, event=None):
        if self.randomwords:
            self.info['randomwords'].set('\n'.join(self.randomwords.words))
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
        editor = wd.MarkdownWindow(top, self.interface.markdown)
        self.wait_window(top)
        self.interface.markdown = editor.markdown

    def edit_styles(self, event=None):
        top = Tk.Toplevel()
        tagger = self.interface.tagger
        wd.StylesWindow(tagger, master=top, name=self.interface.site.name)
        self.wait_window(top)
        self.textbox.add_commands()
        self.interface.config['styles'] = dict(self.interface.tagger.items())

    def show_tags(self):
        self.textbox.show_tags()

    def hide_tags(self):
        self.textbox.hide_tags()

    def show_window(self):
        self.set_window_size(self.top)
        self.master.update()
        self.master.deiconify()
    
    def quit(self):
        self.save_site()
        self.master.quit()

    @property
    def menu_commands(self):
        return [
            ('Site', [
                ('Open', self.open_site),
                ('Save', self.save_site),
                ('Save _As', self.save_site_as)]),
            ('Styles', [
                ('Edit', self.edit_styles),
                ('Apply', self.hide_tags),
                ('Show as Ht_ml', self.show_tags)]),
            ('Markdown', [
                ('Edit', self.markdown_edit),
                ('Clear', self.markdown_clear),
                ('Reset', self.markdown_apply)])]

    # @property
    def textbox_commands(self):
        return [('<Control-r>', self.refresh_random),
                ('<Control-t>', self.open_new_tab),
                ('<Control-T>', self.reopen_tab),
                ('<Control-w>', self.close_tab),
                ('<Enter>', self.reset_entry)]

    @property
    def heading_commands(self):
        return [('<Prior>', self.previous_entry),
                ('<Next>', self.next_entry),
                ('<Return>', self.load_entry)]
