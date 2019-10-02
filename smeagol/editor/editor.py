import json
import re
import time
import tkinter.filedialog as fd
import tkinter.ttk as ttk
import webbrowser as web
from tkinter.ttk import Combobox

from ..widgets import Textbox, StylesWindow
from ..translation import *
from ..utils import *


class Editor(Tk.Frame):
    def __init__(self, master=None, parent=None, text='', tests=None):
        super().__init__(master)
        self.parent = parent
        self.initial_text = text
        self.master.withdraw()
        self.master.protocol('WM_DELETE_WINDOW', self.quit)
        self.setup_linguistics()
        self.ready()
        self.place_widgets()
        if tests:
            tests(self)
        
    def Text(self, text):
        return Text(self, text)

    def set_window_size(self, top):
        top.state('normal')
        w = w_pos = int(top.winfo_screenwidth() / 2)
        h = top.winfo_screenheight()
        h_pos = 0
        top.geometry(f'{w}x{h}+{w_pos}+{h_pos}')

    def ready(self):
        for widget in self.widgets:
            getattr(self, 'ready_' + widget)()
        
    def ready_frames(self):
        self.sidebar = Tk.Frame(self.master)
        self.textframe = Tk.Frame(self.master)
        self.top = self.winfo_toplevel()
        self.set_window_size(self.top)

    def ready_menus(self):
        self.menu = Tk.Menu(self.top)
        for menu in self.menu_commands:
            submenu = Tk.Menu(self.menu, tearoff=0)
            label, options = menu
            self.menu.add_cascade(label=label, menu=submenu)
            for option in options:
                label, command = option
                underline = label.find('_')
                underline = 0 if underline == -1 else underline
                label = label.replace('_', '')
                keypress = label[underline]
                submenu.add_command(label=label, command=command,
                                    underline=underline)
                submenu.bind(f'<KeyPress-{keypress}>', command)

    def ready_labels(self):
        master = self.sidebar
        self.information = Tk.StringVar()
        self.info_label = Tk.Label(
            master=master, textvariable=self.information,
            font=('Arial', 14), width=20)
        self.style_label = Tk.Label(
            master=master, font=('Arial', 12),
            textvariable=self.textbox.style)
        self.blank_label = Tk.Label(master=master, height=1000)

    def ready_option_menu(self):
        self.languagevar.set(self.language)
        translator = self.translator
        languages = [f'{code}: {lang().name}'
                     for code, lang in list(translator.languages.items())]
        self.language_menu = Combobox(self.sidebar,
                                      textvariable=self.languagevar,
                                      values=languages,
                                      height=2000,
                                      width=25,
                                      justify=Tk.CENTER)
        self.language_menu.state(['readonly'])
        self.language_menu.bind('<<ComboboxSelected>>',
                                self.change_language)

    def ready_textbox(self):
        self.textbox = Textbox(self.textframe)
        self.add_commands(self.textbox, self.textbox_commands)
        self.textbox.text = self.initial_text

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

    def setup_linguistics(self):
        self.languagevar = Tk.StringVar()
        self.language = 'en: English'
        self.setup_markdown()
        self.randomwords = RandomWords()
        self.translator = Translator(self.language)

    def setup_markdown(self, filename=None):
        self.marker = Markdown(filename)
        self.markup = self.marker.to_markup
        self.markdown = self.marker.to_markdown

    def change_language(self, event=None):
        self.language = self.languagevar.get()[:2]
        self.translator = Translator(self.language)
        self.randomwords = RandomWords(self.language)
        return 'break'

    def go_to(self, position):
        self.textbox.mark_set(Tk.INSERT, position)
        self.textbox.see(Tk.INSERT)

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

    def place_widgets(self):
        self.top['menu'] = self.menu
        self.pack(expand=True, fill=Tk.BOTH)
        self.sidebar.pack(side=Tk.LEFT)
        self.textframe.pack(side=Tk.RIGHT, expand=True, fill=Tk.BOTH)
        widgets = 'style_label', 'language_menu', 'info_label', 'blank_label'
        for row, widget in enumerate(widgets, start=1):
            getattr(self, widget).grid(row=row, column=0)
        self.textbox.pack(side=Tk.TOP, expand=True, fill=Tk.BOTH)

    def refresh_random(self, event=None):
        if self.randomwords:
            self.information.set('\n'.join(self.randomwords.words))
        return 'break'

    def replace(self, heading, text):
        heading.delete(*Tk.ALL)
        heading.insert(Tk.FIRST, text)

    def clear_interface(self, event=None):
        self.display(self.initial_text)
        self.information.set('')

    def cancel_changes(self, event=None):
        self.clear_interface()
        self.quit()

    def key_released(self, event):
        self.update_wordcount(event)
        if 33 <= event.keycode <= 40:
            event.widget.shift_style()

    def update_wordcount(self, event=None):
        try:
            if event is not None:
                textbox = event.widget
        except AttributeError:
            textbox = event
        self.information.set(textbox.wordcount)

    def display(self, text):
        self.textbox.replace(str(text))
        self.textbox.focus_set()
        self.update_wordcount(self.textbox)
        self._to_tkinter()

    def example_no_lines(self, event):
        self.format_paragraph('example-no-lines', 'e ', event.widget)
        return 'break'

    def example(self, event):
        self.format_paragraph('example', 'f ', event.widget)
        return 'break'

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
        self._to_tkinter()
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
        self._to_tkinter()
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
        styles = self.textbox.styles
        window = StylesWindow(styles)
        self.wait_window(window)
        self.textbox.styles = window.get()
    
    def _to_html(self):
        self.textbox._to_html()
    
    def _to_tkinter(self):
        self.textbox._to_tkinter()

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
                 ('Apply', self._to_tkinter),
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
        return [('<KeyRelease>', self.key_released),
                ('<Escape>', self.cancel_changes),
                ('<Control-d>', self.add_descendant),
                ('<Control-m>', self.markdown_refresh),
                ('<Control-r>', self.refresh_random),
                ('<Control-R>', self.add_translation),
                ('<Control-s>', self._command)]
    
    @property
    def widgets(self):
        return ['frames', 'menus', 'textbox', 'labels', 'option_menu']

    def quit(self):
        # with ignored(AttributeError):
        self._to_html()
        text = self.textbox.get(*Tk.WHOLE_BOX)
        with ignored(AttributeError):
            self.callback(text)
        if self.parent:
            self.parent.show_window()
            self.parent._return = text
        self.master.destroy()
