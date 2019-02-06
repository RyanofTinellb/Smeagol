import re
import tkFont
import Tkinter as Tk
import tkFileDialog as fd
import webbrowser as web
from ttk import Combobox
from itertools import izip
from smeagol.translation import *
from smeagol.utils import ignored, tkinter, is_key

Tk.LINESTART = Tk.INSERT + ' linestart'
Tk.LINEEND = Tk.INSERT + ' lineend'
Tk.CURRLINE = (Tk.LINESTART, Tk.LINEEND)
Tk.UPLINE = Tk.INSERT + ' -1 lines'
Tk.PREVLINE = (Tk.UPLINE + ' linestart', Tk.UPLINE + ' lineend')

BRACKETS = {'[': ']', '<': '>', '{': '}', '"': '"', '(': ')'}

class Editor(Tk.Frame, object):
    def __init__(self, master=None, parent=None):
        super(Editor, self).__init__(master)
        self.master.withdraw()
        self.parent = parent
        self.master.protocol('WM_DELETE_WINDOW', self.quit)
        self.set_frames()
        self.row = 0
        self.font = tkFont.Font(family='Calibri', size=18)
        self.setup_linguistics()
        self.ready()
        self.place_widgets()

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
                submenu.bind('<KeyPress-{0}>'.format(keypress), command)

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
        languages = [u'{0}: {1}'.format(code, lang().name)
                for code, lang in translator.languages.items()]
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
            if isinstance(keys, basestring):
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
        (strong, em, underline, small_caps, highlulani,
         example, example_no_lines) = iter(
                                [self.font.copy() for _ in xrange(7)])
        strong.configure(weight='bold')
        em.configure(slant='italic')
        underline.configure(underline=True, family='Calibri')
        small_caps.configure(
            size=small_caps.actual(option='size') - 3,
            family='Algerian')
        highlulani.configure(
            size=highlulani.actual(option='size') + 3,
            family='Lulani')
        example.configure(size=-1)
        return [
            ('example',
                {'lmargin1': '2c', 'spacing1': '5m', 'font': example}),
            ('example-no-lines', {'lmargin1': '2c', 'font': example}),
            ('strong', {'font': strong}),
            ('em', {'font': em}),
            ('small-caps', {'font': small_caps}),
            ('link', {'foreground': 'blue', 'font': underline}),
            ('bink', {'foreground': 'red', 'font': underline}),
            ('high-lulani', {'font': highlulani})]

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
        self.evolver = HighToDemoticLulani()

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
        pattern = r'\n|[^a-zA-Z0-9_\'-]'
        borders = (
            textbox.search(
                pattern, Tk.INSERT, backwards=True, regexp=True
            ) + '+1c' or Tk.INSERT + ' linestart',
            textbox.search(
                pattern, Tk.INSERT, regexp=True
            ) or Tk.INSERT + ' lineend'
        )
        textbox.tag_add('sel', *borders)
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
            widget.delete(1.0, Tk.END)
            widget.insert(1.0, text)
            widget.mark_set(Tk.INSERT, position)
            widget.mark_set(Tk.CURRENT, position)
            widget.see(Tk.INSERT)
        except Tk.TclError:  # heading
            widget.delete(0, Tk.END)
            widget.insert(0, text)

    def clear_interface(self):
        self.textbox.delete(1.0, Tk.END)
        self.information.set('')

    def edit_text_changed(self, event):
        self.update_wordcount(event)
        key = event.char
        keysym = event.keysym
        textbox = event.widget
        if key.startswith('Control_'):
            textbox.edit_modified(False)
        elif key and is_key(keysym) and event.num == '??':
            style = self.current_style.get()
            with ignored(Tk.TclError):
                textbox.delete(Tk.SEL_FIRST, Tk.SEL_LAST)
            text = key + BRACKETS.get(key, '')
            textbox.insert(Tk.INSERT, text)
            bounds = '{0}-{1}c'.format(Tk.INSERT, len(text))
            textbox.tag_add(style, bounds, Tk.INSERT)
            mark = '{0}-{1}c'.format(Tk.INSERT, len(text) - 1)
            textbox.mark_set(Tk.INSERT, mark)
            return 'break'
        elif keysym == 'Return':
            spaces = re.sub(r'( *).*', r'\1', textbox.get(*Tk.CURRLINE))
            textbox.insert(Tk.INSERT, '\n' + spaces)
            return 'break'
        elif keysym not in {'BackSpace', 'Shift_L', 'Shift_R'}:
            self.current_style.set('')

    def scroll_textbox(self, event=None):
        self.textbox.yview_scroll(-1 * (event.delta / 20), Tk.UNITS)
        return 'break'

    @staticmethod
    def select_all(event):
        event.widget.tag_add('sel', '1.0', 'end')
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

    @tkinter()
    def move_line(self, event):
        if event.keysym == 'Up':
            direction = ' -1 lines'
            correction = ' -1c linestart'
        elif event.keysym == 'Down':
            direction = ' +1 lines'
            correction = ' lineend +1c'
        else:
            return 'break'
        textbox = event.widget
        position = textbox.index(Tk.INSERT)
        try:
            ends = (Tk.SEL_FIRST + ' linestart',
                    Tk.SEL_LAST + ' lineend +1c')
            text = textbox.get(*ends)
            selected = map(textbox.index, (Tk.SEL_FIRST, Tk.SEL_LAST))
        except Tk.TclError:
            ends = (Tk.INSERT + ' linestart',
                    Tk.INSERT + ' lineend +1c')
            text = textbox.get(*ends)
            selected = None
        textbox.delete(*ends)
        textbox.insert(Tk.INSERT + correction, text)
        if selected:
            textbox.tag_add('sel', *map(lambda x: x + direction, selected))
        textbox.mark_set(Tk.INSERT, position + direction)
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
        self.replace(self.textbox, text)
        self.textbox.focus_set()
        self.update_wordcount(widget=self.textbox)
        self.html_to_tkinter()

    def copy_text(self, event=None):
        self._copy(event)
        return 'break'

    @tkinter()
    def _copy(self, event=None):
        textbox = event.widget
        with ignored(Tk.TclError):
            borders = (Tk.SEL_FIRST, Tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(textbox.get(*borders))
        return borders

    @tkinter()
    def cut_text(self, event=None):
        textbox = event.widget
        textbox.delete(*self._copy(event))
        return 'break'

    @tkinter()
    def paste_text(self, event=None):
        textbox = event.widget
        with ignored(Tk.TclError):
            borders = (Tk.SEL_FIRST, Tk.SEL_LAST)
            textbox.delete(*borders)
        textbox.insert(Tk.INSERT, self.clipboard_get())
        return 'break'

    def bold(self, event):
        self.change_style(event, 'strong')
        return 'break'

    def italic(self, event):
        self.change_style(event, 'em')
        return 'break'

    def small_caps(self, event):
        self.change_style(event, 'small-caps')
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
            if other <> 'sel':
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
            borders = (Tk.SEL_FIRST, Tk.SEL_LAST)
            text = textbox.get(*borders)
        except Tk.TclError:
            text = self.select_word(event)
            textbox.tag_remove('sel', '1.0', Tk.END)
        length = len(text)
        text = self.markup(text)
        example = re.match(r'\[[ef]\]', text)  # line has 'example' formatting
        converter = self.translator.convert_word # default setting
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
            borders = (Tk.SEL_FIRST, Tk.SEL_LAST)
            text = textbox.get(*borders)
        except Tk.TclError:
            text = self.select_word(event)
            textbox.tag_remove('sel', '1.0', Tk.END)
        length = len(text)
        text = self.markup(text)
        example = re.match(r'\[[ef]\]', text)  # line has 'example' formatting
        converter = self.evolver.evolve # default setting
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
        for (style, _) in self.text_styles:
            while True:
                try:
                    if style.startswith('example'):
                        letter = 'e' if style.endswith('lines') else 'f'
                        start = textbox.search(
                            '\[[{0}]\]'.format(letter),
                            '1.0',
                            regexp=True,
                            count=count
                        )
                        end = '{0}+3c'.format(start)
                        text = textbox.get(start, end)
                        text = text[1] + ' '
                        textbox.delete(start, end)
                        textbox.insert(start, text)
                        textbox.tag_add(
                            style, start, '{0}+{1}c'.format(start, len(text)))
                    else:
                        start = textbox.search(
                            '<{0}>.*?</{0}>'.format(style),
                            '1.0',
                            regexp=True,
                            count=count
                        )
                        end = '{0}+{1}c'.format(start, count.get())
                        text = textbox.get(start, end)
                        text = text[(len(style) + 2):(-3 - len(style))]
                        textbox.delete(start, end)
                        textbox.insert(start, text)
                        textbox.tag_add(style, start,
                                        '{0}+{1}c'.format(start, len(text)))
                except Tk.TclError:
                    break
        self.reset_textbox()

    def tkinter_to_html(self, event=None):
        textbox = self.textbox
        for (style, _) in self.text_styles:
            for end, start in izip(*[reversed(textbox.tag_ranges(style))] * 2):
                if style.startswith('example'):
                    text = textbox.get(start, end)[0]
                    text = '[{0}]'.format(text)
                else:
                    text = textbox.get(start, end)
                    text = '<{1}>{0}</{1}>'.format(text, style)
                textbox.delete(start, end)
                textbox.insert(start, text)

    def markdown_open(self, event=None):
        web.open_new_tab(self.marker.filename)

    def markdown_load(self, event=None):
        filename = fd.askopenfilename(
            filetypes=[('Sm\xe9agol Markdown File', '*.mkd')],
            title='Load Markdown')
        if filename:
            try:
                self._markdown_load(filename)
            except IndexError:
                mb.showerror('Invalid File',
                             'Please select a valid *.mkd file.')

    @tkinter()
    def _markdown_load(self, filename):
        text = self.get_text(self.textbox)
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
        text = self.get_text(self.textbox)
        text = self.markup(text)
        self.marker.refresh(new_markdown)
        text = self.markdown(text)
        self.replace(self.textbox, text)

    @tkinter()
    def markdown_clear(self, event=None):
        text = self.get_text(self.textbox)
        text = self.markup(text)
        self.replace(self.textbox, text)

    def markdown_edit(self, event=None):
        text = self.edit_file(text=str(self.marker))
        self.markdown_refresh(new_markdown=text)

    def edit_file(self, text=''):
        # editor returns a value in self._return
        self.show_file(text)
        return self._return

    def show_file(self, text=''):
        top = Tk.Toplevel()
        editor = Editor(master=top, parent=self)
        editor.textbox.insert(Tk.INSERT, text)
        self.master.withdraw()
        self.wait_window(top)

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
            ('<Control-k>', self.small_caps),
            ('<Control-K>', self.delete_line),
            ('<Control-m>', self.markdown_refresh),
            ('<Control-n>', self.add_link),
            ('<Control-r>', self.refresh_random),
            ('<Control-s>', self.tkinter_to_html),
            ('<Control-t>', self.add_translation),
            ('<Control-v>', self.paste_text),
            ('<Control-w>', self.select_word),
            ('<Control-x>', self.cut_text),
            ('<Control-BackSpace>', self.backspace_word),
            ('<Control-Delete>', self.delete_word),
            (('<Control-Up>', '<Control-Down>'), self.move_line)]

    def quit(self):
        # with ignored(AttributeError):
        self.tkinter_to_html()
        self.parent.show_window()
        self.parent._return = self.textbox.get('1.0', Tk.END)
        self.master.destroy()

if __name__ == '__main__':
    Editor().mainloop()
