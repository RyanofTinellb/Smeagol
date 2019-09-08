import json
import re
import time
import tkinter.filedialog as fd
import tkinter.ttk as ttk
import webbrowser as web
from tkinter.font import Font
from tkinter.ttk import Combobox

from ..translation import *
from ..utils import *


class Editor(Tk.Frame):
    def __init__(self, master=None, parent=None, text='', tests=None):
        super().__init__(master)
        self.parent = parent
        self.initial_text = text
        self.master.withdraw()
        self.master.protocol('WM_DELETE_WINDOW', self.quit)
        self.set_frames()
        self.row = 1
        self.font = Font(family='Calibri', size=18)
        self.setup_linguistics()
        self.ready()
        self.place_widgets()
        if tests:
            tests(self)
 
    def set_frames(self):
        self.sidebar = Tk.Frame(self.master)
        self.textframe = Tk.Frame(self.master)
        self.top = self.winfo_toplevel()
        self.top.state('zoomed')

    def ready(self):
        objs = ['menus', 'labels', 'option_menu', 'textbox']
        for obj in objs:
            getattr(self, 'ready_' + obj)()

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
        self.current_style = Tk.StringVar()
        self.current_style.set('')
        self.style_label = Tk.Label(
            master=master, font=('Arial', 12),
            textvariable=self.current_style)
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
        master = self.textframe
        font = self.font
        self.textbox = Tk.Text(master, height=1, width=1, wrap=Tk.WORD,
                               undo=True, font=font)
        self.add_commands(self.textbox, self.textbox_commands)
        self.ready_scrollbar()
        for (name, style) in self.text_styles:
            self.textbox.tag_config(name, **style)
        self.textbox.insert(Tk.START, self.initial_text)

    def reset_textbox(self):
        self.textbox.edit_modified(False)
        self.textbox.config(font=self.font)
        for (name, style) in self.text_styles:
            self.textbox.tag_config(name, **style)

    def ready_scrollbar(self):
        scrollbar = Tk.Scrollbar(self.textframe)
        scrollbar.pack(side=Tk.RIGHT, fill=Tk.Y)
        scrollbar.config(command=self.textbox.yview)
        self.textbox.config(yscrollcommand=scrollbar.set)

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

    @property
    def text_styles(self):
        (strong, em, underline, small_caps, tinellbian,
         example, ipa) = iter(
            [self.font.copy() for _ in range(7)])
        strong.configure(weight='bold')
        em.configure(slant='italic')
        underline.configure(underline=True, family='Calibri')
        small_caps.configure(
            family='Alegreya SC')
        tinellbian.configure(
            size=tinellbian.actual(option='size') + 3,
            family='Tinellbian')
        example.configure(size=-1)
        ipa.configure(
            family='lucida sans unicode')
        return [
            ('example',
                {'lmargin1': '2c', 'spacing1': '5m', 'font': example}),
            ('example-no-lines', {'lmargin1': '2c', 'font': example}),
            ('strong', {'font': strong}),
            ('em', {'font': em}),
            ('small-caps', {'font': small_caps}),
            ('link', {'foreground': 'blue', 'font': underline}),
            ('bink', {'foreground': 'red', 'font': underline}),
            ('high-lulani', {'font': tinellbian}),
            ('ipa', {'font': ipa})]

    def modify_fontsize(self, size):
        self.font.config(size=size)
        self.textbox.config(font=self.font)
        for (name, style) in self.text_styles:
            self.textbox.tag_config(name, **style)

    def change_fontsize(self, event):
        sign = 1 if event.delta > 0 else -1
        size = self.font.actual(option='size') + sign
        self.modify_fontsize(size)
        return 'break'

    def reset_fontsize(self, event):
        self.modify_fontsize(18)
        return 'break'

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
        self.style_label.grid(row=1, column=0)
        self.language_menu.grid(row=2, column=0)
        self.info_label.grid(row=3, column=0)
        self.blank_label.grid(row=4, column=0)
        self.textbox.pack(side=Tk.TOP, expand=True, fill=Tk.BOTH)

    def refresh_random(self, event=None):
        if self.randomwords:
            self.information.set('\n'.join(self.randomwords.words))
        return 'break'

    def replace(self, widget, text):
        try:  # textbox
            position = widget.index(Tk.INSERT)
            widget.delete(*Tk.WHOLE_BOX)
            widget.insert(Tk.START, text)
            widget.mark_set(Tk.INSERT, position)
            widget.see(Tk.INSERT)
        except Tk.TclError:  # heading
            widget.delete(*Tk.WHOLE_ENTRY)
            widget.insert(Tk.FIRST, text)

    def clear_interface(self, event=None):
        position = self.textbox.index(Tk.INSERT)
        self.display(self.initial_text)
        self.textbox.mark_set(Tk.INSERT, position)
        self.information.set('')
    
    def escape(self, event=None):
        self.clear_interface()
        self.quit()

    def edit_text_changed(self, event):
        self.update_wordcount(event)
        key = event.char
        keysym = event.keysym
        code = event.keycode
        textbox = event.widget
        if key.startswith('Control_') or key == '??':
            textbox.edit_modified(False)
        elif key and key == keysym and event.num == '??':
            style = self.current_style.get()
            match = BRACKETS.get(key, '')
            if match:
                try:
                    textbox.insert(Tk.SEL_FIRST, key)
                    textbox.insert(Tk.SEL_LAST, match)
                except Tk.TclError:
                    textbox.insert(Tk.INSERT, key + match)
                    move_mark(textbox, Tk.INSERT, -1)
            else:
                try:
                    textbox.delete(*Tk.SELECTION)
                    textbox.insert(Tk.SEL, key, style)
                except Tk.TclError:
                    textbox.insert(Tk.INSERT, key, style)
            return 'break'
        elif keysym == 'Return':
            spaces = re.sub(r'( *).*', r'\1', textbox.get(*Tk.CURRLINE))
            textbox.insert(Tk.INSERT, spaces)
            return 'break'
        elif keysym not in {'BackSpace', 'Shift_L', 'Shift_R'}:
            self.current_style.set('')

    def scroll_textbox(self, event=None):
        self.textbox.yview_scroll(int(-1 * (event.delta / 20)), Tk.UNITS)
        return 'break'

    @staticmethod
    def select_all(event):
        event.widget.tag_add(Tk.SEL, '1.0', Tk.END)
        return 'break'

    def backspace_word(self, event):
        widget = event.widget
        get = widget.get
        if get(Tk.INSERT + '-1c') in '.,;:?! ':
            correction = '-2c wordstart'
        elif get(Tk.INSERT) in ' ':
            correction = '-1c wordstart -1c'
        else:
            correction = '-1c wordstart'
        widget.delete(Tk.INSERT + correction, Tk.INSERT)
        self.update_wordcount(event)
        return 'break'

    def delete_word(self, event):
        widget = event.widget
        get = widget.get
        if (
            get(Tk.INSERT + '-1c') in ' .,;:?!\n' or
            widget.compare(Tk.INSERT, '==', '1.0')
        ):
            correction = ' wordend +1c'
        elif get(Tk.INSERT) == ' ':
            correction = '+1c wordend'
        elif get(Tk.INSERT) in '.,;:?!':
            correction = '+1c'
        else:
            correction = ' wordend'
        widget.delete(Tk.INSERT, Tk.INSERT + correction)
        self.update_wordcount(event)
        return 'break'

    def delete_line(self, event=None):
        try:
            event.widget.delete(Tk.SEL_FIRST + ' linestart',
                                Tk.SEL_LAST + ' lineend +1c')
        except Tk.TclError:
            event.widget.delete(Tk.LINESTART,
                                Tk.LINEEND + ' +1c')
        return 'break'

    def update_wordcount(self, event=None, widget=None):
        if event is not None:
            widget = event.widget
        text = widget.get(1.0, Tk.END)
        self.information.set(
            str(text.count(' ') + text.count('\n') - text.count(' | ')))

    def display(self, text):
        self.replace(self.textbox, str(text))
        self.textbox.focus_set()
        self.update_wordcount(widget=self.textbox)
        self.html_to_tkinter()

    def move_line(self, event):
        tb = event.widget # textbox
        tb.insert(Tk.END, '\n') # ensures last line can be moved normally
        if tb.compare(Tk.END, '==', Tk.INSERT): # ensures last line can be
            tb.mark_set(Tk.INSERT, f'{Tk.END}-1c') #  moved from the last char.
        location = Tk.PREV_LINE if event.keysym == 'Up' else Tk.NEXT_LINE
        try:
            borders, text = self._cut(tb, Tk.SEL_LINE, False)
            self._paste(tb, location, Tk.NO_SELECTION, text)
        except Tk.TclError:
            borders, text = self._cut(tb, Tk.CURRLINE, False)
            self._paste(tb, location, Tk.NO_SELECTION, text)
        tb.mark_set(Tk.INSERT, Tk.USER_MARK)
        tb.delete(f'{Tk.END}-1c') # removes helper newline
        return 'break'

    def copy_text(self, event=None):
        with ignored(Tk.TclError):
            self._copy(event.widget, Tk.SELECTION)
        return 'break'

    def _copy(self, textbox, borders=None, clip=True):
        '''@error: raise Tk.TclError if no text is selected'''
        borders = borders or Tk.SELECTION
        text = '\x08' + json.dumps(textbox.dump(*borders),
            ensure_ascii=False).replace('],', '],\n')
        if clip:
            self.clipboard_clear()
            self.clipboard_append(text)
        return borders, text

    def cut_text(self, event=None):
        with ignored(Tk.TclError):
            self._cut(event.widget, Tk.SELECTION)
        return 'break'
    
    def _cut(self, textbox, borders=None, clip=True):
        '''@error: raise Tk.TclError if no text is selected'''
        borders, text = self._copy(textbox, borders, clip)
        textbox.delete(*borders)
        return borders, text
    
    def paste_text(self, event=None):
        textbox = event.widget
        try:
            self._paste(event.widget, Tk.INSERT, Tk.SELECTION)
        except Tk.TclError:
            self._paste(event.widget, Tk.INSERT, Tk.NO_SELECTION)
        with ignored(Tk.TclError):
            textbox.tag_remove(Tk.SEL, *Tk.WHOLE_BOX)
        return 'break'

    def _paste(self, textbox, location=None, borders=None, text=None):
        '''@error: raise Tk.TclError if no text is selected'''
        location = location or Tk.INSERT
        borders = borders or Tk.SELECTION
        textbox.delete(*borders)
        textbox.mark_set(Tk.INSERT, location)
        if not text:
            try:
                text = self.clipboard_get()
            except Tk.TclError:
                return
        if text.startswith('\x08'):
            tag = ''
            sel = ''
            tags = json.loads(text[1:])
            for key, value, index in tags:
                if key == 'mark' and value == Tk.INSERT:
                    textbox.mark_set(Tk.USER_MARK, Tk.INSERT)
                    textbox.mark_gravity(Tk.USER_MARK, Tk.LEFT)
                if key == 'tagon':
                    if value == Tk.SEL:
                        sel = Tk.SEL
                    else:
                        tag = value
                elif key == 'text':
                    textbox.insert(Tk.INSERT, value, (tag, sel))
                elif key == 'tagoff':
                    if value == Tk.SEL:
                        sel = ''
                    else:
                        tag = ''
        else:
            textbox.insert(Tk.INSERT, text)
        textbox.tag_remove('', *Tk.WHOLE_BOX)

    def bold(self, event):
        self.change_style(event, 'strong')
        return 'break'

    def italic(self, event):
        self.change_style(event, 'em')
        return 'break'

    def small_caps(self, event):
        self.change_style(event, 'small-caps')
        return 'break'

    def ipa(self, event):
        self.change_style(event, 'ipa')
        return 'break'

    def add_link(self, event):
        self.change_style(event, 'link')
        return 'break'

    def insert_tabs(self, event=None):
        self.textbox.insert(Tk.LINESTART, ' ' * 4)
        return 'break'

    def remove_tabs(self, event=None):
        if self.textbox.get(Tk.LINESTART, Tk.LINEEND).startswith(' ' * 4):
            self.textbox.delete(Tk.LINESTART, Tk.LINESTART + '+4c')
        return 'break'

    def change_style(self, event, style):
        textbox = event.widget
        for other in textbox.tag_names():
            if other != Tk.SEL:
                with ignored(Tk.TclError):
                    textbox.tag_remove(other, Tk.SEL_FIRST, Tk.SEL_LAST)
        if style == self.current_style.get():
            self.current_style.set('')
        else:
            self.current_style.set(style)
            with ignored(Tk.TclError):
                textbox.tag_add(style, Tk.SEL_FIRST, Tk.SEL_LAST)

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
        self.html_to_tkinter()
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
        self.html_to_tkinter()
        return 'break'

    def html_to_tkinter(self):
        count = Tk.IntVar()
        textbox = self.textbox
        texts = re.split(r'(\[[ef] *\]|<.*?>)', get_text(textbox))
        paras = dict(e='example-no-lines', f='example')
        styles = {'em', 'strong', 'high-lulani', 'small-caps', 'link', 'bink',
            'ipa'}
        tag = None
        ins = ''
        textbox.delete(1.0, Tk.END)
        for text in texts:
            if re.match(r'\[[ef] *\]', text):
                textbox.insert(Tk.INSERT, f'{text[1]} ', paras[text[1]])
                continue
            else:
                new_tag = re.sub(r'</*(.*?)>', r'\1', text)
                if text.startswith('</'):
                    if new_tag in styles:
                        tag = None
                        ins = ''
                    else:
                        ins = text
                elif text.startswith('<'):
                    if new_tag in styles:
                        tag = new_tag
                        ins = ''
                    else:
                        ins = text
                else:
                    ins = text
            textbox.insert(Tk.INSERT, ins, tag)
        self.reset_textbox()

    def tkinter_to_html(self, event=None):
        textbox = self.textbox
        for (style, _) in self.text_styles:
            for end, start in zip(*[reversed(textbox.tag_ranges(style))] * 2):
                if style.startswith('example'):
                    text = textbox.get(start, end)[0]
                    text = f'[{text}]'
                else:
                    text = textbox.get(start, end)
                    text = '<{1}>{0}</{1}>'.format(text, style)
                textbox.delete(start, end)
                textbox.insert(start, text)

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
        text = get_text(self.textbox)
        text = self.markup(text)
        self.setup_markdown(filename)
        text = self.markdown(text)
        self.replace(self.textbox, text)

    def markdown_refresh(self, event=None, new_markdown=''):
        try:
            self._markdown_refresh(new_markdown)
            self.information.set('OK')
        except AttributeError:
            self.information.set('Not OK')
        return 'break'

    @tkinter()
    def _markdown_refresh(self, new_markdown):
        text = get_text(self.textbox)
        text = self.markup(text)
        self.marker.refresh(new_markdown)
        text = self.markdown(text)
        self.replace(self.textbox, text)

    @tkinter()
    def markdown_clear(self, event=None):
        text = get_text(self.textbox)
        text = self.markup(text)
        self.replace(self.textbox, text)

    def markdown_edit(self, event=None):
        text = self.edit_file(text=str(self.marker))
        self.markdown_refresh(new_markdown=text)

    def edit_file(self, text='', command=None):
        # editor returns a value in self._return
        self.show_file(text, command)
        return self._return

    def show_file(self, text='', command=None):
        top = Tk.Toplevel()
        editor = Editor(master=top, parent=self, text=text)
        if command:
            editor.exit_command = command
        self.master.withdraw()
        self.wait_window(top)

    def _command(self, event=None):
        self.tkinter_to_html()
        text = self.textbox.get('1.0', Tk.END)
        with ignored(AttributeError):
            self.exit_command(text)
            self.information.set('Saved!')

    def show_window(self):
        self.top.state('zoomed')
        self.master.update()
        self.master.deiconify()

    @property
    def menu_commands(self):
        return [('Markdown', [
                 ('Edit', self.markdown_edit),
                 ('Clear', self.markdown_clear),
                 ('Load', self.markdown_load),
                 ('Refresh', self.markdown_refresh),
                 ('Change to _Tkinter', self.html_to_tkinter),
                 ('Change to Ht_ml', self.tkinter_to_html),
                 ('Open as _Html', self.markdown_open)])]

    @property
    def textbox_commands(self):
        return [
            ('<MouseWheel>', self.scroll_textbox),
            ('<Control-MouseWheel>', self.change_fontsize),
            (('<KeyPress>', '<Button-1>'), self.edit_text_changed),
            ('<Escape>', self.escape),
            ('<Tab>', self.insert_tabs),
            ('<Shift-Tab>', self.remove_tabs),
            ('<Control-0>', self.reset_fontsize),
            ('<Control-a>', self.select_all),
            ('<Control-b>', self.bold),
            ('<Control-c>', self.copy_text),
            ('<Control-d>', self.add_descendant),
            ('<Control-e>', self.example_no_lines),
            ('<Control-f>', self.example),
            ('<Control-i>', self.italic),
            ('<Control-I>', self.ipa),
            ('<Control-k>', self.small_caps),
            ('<Control-K>', self.delete_line),
            ('<Control-m>', self.markdown_refresh),
            ('<Control-n>', self.add_link),
            ('<Control-r>', self.refresh_random),
            ('<Control-s>', self._command),
            # ('<Control-t>', self.add_translation),
            ('<Control-v>', self.paste_text),
            ('<Control-x>', self.cut_text),
            # ('<Control-y>', self.redo),
            # ('<Control-z>', self.undo),
            ('<Control-BackSpace>', self.backspace_word),
            ('<Control-Delete>', self.delete_word),
            (('<Control-Up>', '<Control-Down>'), self.move_line)]

    def quit(self):
        # with ignored(AttributeError):
        self.tkinter_to_html()
        text = self.textbox.get(*Tk.WHOLE_BOX)
        with ignored(AttributeError):
            self.exit_command(text)
        if self.parent:
            self.parent.show_window()
            self.parent._return = text
        self.master.destroy()