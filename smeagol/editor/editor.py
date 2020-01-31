import json
import re
import time
import tkinter.filedialog as fd
import tkinter.ttk as ttk
import webbrowser as web
from tkinter.ttk import Combobox

from ..widgets import Textbox, StylesWindow, Style, Styles
from ..translation import *
from ..utils import *


class Editor(Tk.Frame):
    def __init__(self, master=None, parent=None, styles=None, tests=None):
        super().__init__(master)
        self.parent = parent
        self.master.withdraw()
        self.master.protocol('WM_DELETE_WINDOW', self.quit)
        self.styles = Styles(styles)
        self.closed_tabs = []
        self.create_layout(self.master)
        self.setup_markdown()
        self.open_tab()
        if tests:
            tests(self)

    def Text(self, text):
        return Text(self, text)

    def __getattr__(self, attr):
        if attr == 'tab':
            return self.notebook.nametowidget(self.notebook.select())
        if attr == 'textbox':
            return self.tab.textbox
        else:
            return getattr(super(), attr)

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

    def new_textbox(self, master):
        textbox = Textbox(master, self.styles)
        self.add_commands(textbox, self.textbox_commands)
        return textbox
        
    def sidebar(self, master):
        frame = Tk.Frame(master)
        self.displays = dict(
            wordcount=Tk.Label(master=frame, font=('Arial', 14), width=20),
            style=Tk.Label(master=frame, font=('Arial', 12)),
            language=self.language_display(frame),
            randomwords=self.random_words_display(frame),
            blank=Tk.Label(master=frame, height=1000))
        for row, display in enumerate(self.displays.values(), start=1):
            display.grid(row=row, column=0)
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
        translator = Translator()
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

    def setup_markdown(self, filename=None):
        self.marker = Markdown(filename)
        self.markup = self.marker.to_markup
        self.markdown = self.marker.to_markdown

    def change_language(self, event=None):
        language = self.info['language'].get()[:2]
        self.translator = Translator(language)
        self.randomwords = RandomWords(language)
        return 'break'

    def go_to(self, position):
        self.textbox.mark_set(Tk.INSERT, position)
        self.textbox.see(Tk.INSERT)
    
    def open_tab(self, event=None):
        notebook = self.notebook
        frame = Tk.Frame(notebook)
        textbox = self.new_textbox(frame)
        textbox.pack(side=Tk.LEFT, expand=True, fill=Tk.BOTH)
        frame.textbox = textbox
        notebook.add(frame)
        notebook.select(frame)
        return 'break'

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

    def cancel_changes(self, event=None):
        self.information.set('')
        self.clear_interface()
        self.quit()

    def display(self, text):
        self.textbox.replace(str(text))
        self.textbox.focus_set()
        self.update_wordcount(self.textbox)
        self._from_html()

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

    def add_translation(self, event):
        textbox = event.widget
        try:
            borders = Tk.SELECTION
            text = textbox.get(*borders)
        except Tk.TclError:
            text = self.select_word(event)
            textbox.tag_remove(Tk.SEL, '1.0', Tk.END)
        length = len(text)
        text = self.markup(text)
        example = re.match(r'\[[ef]\]', text)  # line has 'example' formatting
        converter = self.translator.convert_word  # default setting
        for mark in '.!?':
            if mark in text:
                converter = self.translator.convert_word
                break
        text = converter(text)
        if example:
            text = '[e]' + text
        self.markdown(text)
        try:
            text += '\n' if textbox.compare(Tk.SEL_LAST,
                                            '==', Tk.SEL_LAST + ' lineend') else ' '
            textbox.insert(Tk.SEL_LAST + '+1c', text)
        except Tk.TclError:
            text += ' '
            textbox.mark_set(Tk.INSERT, Tk.INSERT + ' wordend')
            textbox.insert(Tk.INSERT + '+1c', text)
        self._from_html()
        return 'break'

    def add_descendant(self, event):
        textbox = event.widget
        try:
            borders = Tk.SELECTION
            text = textbox.get(*borders)
        except Tk.TclError:
            text = self.select_word(event)
            textbox.tag_remove(Tk.SEL, '1.0', Tk.END)
        length = len(text)
        text = self.markup(text)
        example = re.match(r'\[[ef]\]', text)  # line has 'example' formatting
        converter = self.evolver.evolve  # default setting
        text = converter(text)[-1]
        if example:
            text = '[e]' + text
        text = self.markdown(text)
        try:
            text += '\n' if textbox.compare(Tk.SEL_LAST,
                                            '==', Tk.SEL_LAST + ' lineend') else ' '
            textbox.insert(Tk.SEL_LAST + '+1c', text)
        except Tk.TclError:
            text += ' '
            textbox.mark_set(Tk.INSERT, Tk.INSERT + ' wordend')
            textbox.insert(Tk.INSERT + '+1c', text)
        self._from_html()
        return 'break'

    def markdown_open(self, event=None):
        web.open_new_tab(self.marker.filename)

    def markdown_load(self, event=None):
        filename = fd.askopenfilename(
            filetypes=[('Sméagol Markdown File', '*.mkd')],
            title='Load Markdown',
            defaultextension='.mkd')
        if filename:
            self._markdown_load(filename)

    @tkinter()
    def _markdown_load(self, filename):
        text = self.Text(self.textbox.text).markup
        self.markdown_file = filename
        self.setup_markdown()
        self.textbox.replace(text.markdown)

    def markdown_refresh(self, event=None, new_markdown=None):
        try:
            self._markdown_refresh(new_markdown)
            self.information.set('OK')
        except AttributeError:
            self.information.set('Not OK')
        return 'break'

    @tkinter()
    def _markdown_refresh(self, new_markdown=None):
        text = self.Text(self.textbox.text).markup
        self.marker.refresh(new_markdown)
        self.textbox.replace(text.markdown)

    @tkinter()
    def markdown_clear(self, event=None):
        self.textbox.replace(self.Text(self.textbox.text).markup)

    @tkinter()
    def markdown_reset(self, event=None):
        self.textbox.replace(self.Text(self.textbox.text).markdown)

    def markdown_edit(self, event=None):
        text = self.edit_file(text=str(self.marker))
        self.markdown_refresh(new_markdown=text)

    def edit_file(self, text='', callback=None):
        # editor returns a value in self._return
        self.show_file(text, callback)
        return self._return

    def show_file(self, text='', callback=None):
        top = Tk.Toplevel()
        editor = Editor(master=top, parent=self, text=text)
        if callback:
            editor.callback = callback
        self.master.withdraw()
        self.wait_window(top)

    def edit_styles(self, event=None):
        top = Tk.Toplevel()
        styles = self.textbox.styles
        window = StylesWindow(styles, master=top)
        self.wait_window(top)
        self.textbox.add_commands()

    def _to_html(self):
        self.textbox._to_html()

    def _from_html(self):
        self.textbox._from_html()

    def _command(self, event=None):
        self._to_html()
        text = self.textbox.get('1.0', Tk.END)
        with ignored(AttributeError):
            self.callback(text)
            self.information.set('Saved!')

    def show_window(self):
        self.set_window_size(self.top)
        self.master.update()
        self.master.deiconify()

    @property
    def menu_commands(self):
        return [('Styles', [
                 ('Edit', self.edit_styles),
                 ('Apply', self._from_html),
                 ('Show as Ht_ml', self._to_html)]),
                ('Markdown', [
                 ('Edit', self.markdown_edit),
                 ('Clear', self.markdown_clear),
                 ('Reset', self.markdown_reset),
                 ('Load', self.markdown_load),
                 ('Refresh', self.markdown_refresh),
                 ('Open as _Html', self.markdown_open)])]

    @property
    def textbox_commands(self):
        return [('<Escape>', self.cancel_changes),
                ('<Control-d>', self.add_descendant),
                ('<Control-m>', self.markdown_refresh),
                ('<Control-r>', self.refresh_random),
                ('<Control-R>', self.add_translation),
                ('<Control-s>', self._command),
                ('<Control-t>', self.open_tab),
                ('<Control-T>', self.reopen_tab),
                ('<Control-w>', self.close_tab)]

    def quit(self):
        # with ignored(AttributeError):
        self._to_html()
        text = self.textbox.get()
        with ignored(AttributeError):
            self.callback(text)
        if self.parent:
            self.parent.show_window()
            self.parent._return = text
        self.master.destroy()
