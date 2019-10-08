import re
import json
import tkinter as Tk
from tkinter.scrolledtext import ScrolledText
from tkinter.font import Font
from ..utils import ignored
from .style import Style

START = '1.0'
END = 'end-1c'
ALL = START, END
INSERT = 'insert'
LINESTART = 'insert linestart'
LINEEND = 'insert lineend+1c'
CURRLINE = LINESTART, LINEEND
PREV_LINE = 'insert linestart -1l'
PREVLINE = f'{PREV_LINE} lineend'
NEXT_LINE = 'insert linestart +1l'
SELECTION = 'sel.first', 'sel.last'
SEL_LINE = 'sel.first linestart', 'sel.last lineend+1c'
NO_SELECTION = (INSERT,) * 2
USER_MARK = 'usermark'

BRACKETS = {'[': ']', '<': '>', '{': '}', '"': '"', '(': ')'}


class Textbox(Tk.Text):
    def __init__(self, master, font='Calibri'):
        self.font = Font(family=font, size=18)
        super().__init__(master, height=1, width=1, wrap=Tk.WORD,
                         undo=True, font=self.font)
        self.ready()

    def __getattr__(self, attr):
        if attr == 'text':
            return self.get()
        elif attr == 'current_styles':
            return self.style.get().split()
        else:
            return getattr(super(), attr)

    def __setattr__(self, attr, value):
        if attr == 'text':
            self.replace(value)
        else:
            super().__setattr__(attr, value)

    def _add_style(self, name):
        styles = set(self.current_styles)
        styles.add(name)
        self.style.set(' '.join(styles))

    def _remove_style(self, name):
        styles = set(self.current_styles)
        styles.discard(name)
        self.style.set(' '.join(styles))

    def ready(self):
        self.add_commands()
        self.style = Tk.StringVar()
        self.set_styles()

    def set_styles(self):
        self.style.set('')
        for styleset in zip(self.styles(), ('default', 'font', 'paragraph')):
            self._set_styles(*styleset)

    def _set_styles(self, styles, group='default'):
        for style in styles:
            style.group = group
            name = style.name
            key = style.key
            font = style.Font
            self.tag_config(name, font=font, **style.paragraph)
            if key:
                def command(event, name=name, style=style):
                    print(style)
                    self.change_style(name)
                    return 'break'
                self.bind(f'<Control-{key}>', command)

    def add_commands(self):
        for keys, command in self.commands:
            if isinstance(keys, str):
                self.bind(keys, command)
            else:
                for key in keys:
                    self.bind(key, command)

    def change_style(self, name):
        if name in self.current_styles:
            self._remove_style(name)
            with ignored(Tk.TclError):
                self.tag_remove(name, *SELECTION)
        else:
            self._add_style(name)
            with ignored(Tk.TclError):
                self.tag_add(name, *SELECTION)
        return 'break'

    @property
    def wordcount(self):
        text = self.text
        return text.count(' ') + text.count('\n') - text.count('|')

    @property
    def formatted_text(self):
        return self.formatted_get()

    def get(self, start=START, end=END):
        return super().get(start, end)

    def get_char(self, position=INSERT):
        return super().get(position)

    def formatted_get(self, start=START, end=END):
        return super().dump(start, end)

    def reset(self):
        self.edit_modified(False)
        self.config(font=self.font)
        self.set_styles()

    def replace(self, text, start=START, end=END):
        self.delete(start, end)
        self.insert(text, start)

    def insert(self, text='', position=INSERT, tags=None):
        try:
            super().insert(position, text, tags)
        except Tk.TclError:
            super().insert(text, position, tags)

    def delete(self, start=START, end=END):
        super().delete(start, end)

    def clear(self):
        self.delete()

    def shift_style(self):
        if self.style.get() not in self.tag_names(INSERT):
            self.style.set('')

    def _to_tkinter(self):
        texts = re.split(r'(\[[ef] *\]|<.*?>)', self.text)
        paras = dict(e='example-no-lines', f='example')
        styles = {'em', 'strong', 'high-lulani', 'small-caps', 'link', 'bink',
                  'ipa'}
        tag = None
        txt = ''
        self.clear()
        for text in texts:
            if re.match(r'\[[ef] *\]', text):
                self.insert(f'{text[1]} ', tags=paras[text[1]])
                continue
            else:
                new_tag = re.sub(r'</*(.*?)>', r'\1', text)
                if text.startswith('</'):
                    if new_tag in styles:
                        tag = None
                        txt = ''
                    else:
                        txt = text
                elif text.startswith('<'):
                    if new_tag in styles:
                        tag = new_tag
                        txt = ''
                    else:
                        txt = text
                else:
                    txt = text
            self.insert(txt, tags=tag)
        self.reset()

    def _to_html(self, event=None):
        for style, _, _ in self.styles:
            for start, end in zip(*[iter(self.tag_ranges(style))] * 2):
                if style.startswith('example'):
                    text = self.get(start, end)[0]
                    text = f'[{text}]'
                else:
                    text = self.get(start, end)
                    text = '<{1}>{0}</{1}>'.format(text, style)
                self.delete(start, end)
                self.insert(text, start)

    def modify_fontsize(self, size):
        self.font.config(size=size)
        self.config(font=self.font)
        for (name, key, style) in self.styles:
            self.tag_config(name, **style)

    def change_fontsize(self, event):
        sign = 1 if event.delta > 0 else -1
        size = self.font.actual(option='size') + sign
        self.modify_fontsize(size)
        return 'break'

    def reset_fontsize(self, event):
        self.modify_fontsize(18)
        return 'break'

    def indent(self, event):
        spaces = re.match(r'^ *', self.get(*CURRLINE)).group(0)
        self.insert('\n' + spaces)
        return 'break'

    def move_mark(self, mark, size):
        sign = '+' if size >= 0 else '-'
        size = abs(size)
        self.mark_set(INSERT, mark)
        self.mark_set(mark, f'{mark}{sign}{size}c')

    def insert_characters(self, event):
        key = event.char
        keysym = event.keysym
        code = event.keycode
        styles = self.style.get()
        if key.startswith('Control_'):
            self.edit_modified(False)
        elif key and key == keysym and event.num == '??':
            if not self.match_brackets(key):
                try:
                    self.delete(*SELECTION)
                    self.insert(key, Tk.SEL, tags=self.style.get())
                except Tk.TclError:
                    self.insert(key, tags=self.style.get())
            return 'break'
        elif keysym == 'Return':
            spaces = re.sub(r'( *).*', r'\1', self.get(*CURRLINE))
            self.insert(spaces, INSERT)
            return 'break'
        elif keysym not in {'BackSpace', 'Shift_L', 'Shift_R'}:
            self.style.set('')

    def match_brackets(self, key):
        if key in BRACKETS:
            try:
                self.insert(key, Tk.SEL_FIRST, tags=self.current_styles)
                self.insert(BRACKETS[key], Tk.SEL_LAST,
                            tags=self.current_styles)
            except Tk.TclError:
                self.insert(key + BRACKETS[key], tags=self.current_styles)
                self.move_mark(INSERT, -1)
            return True
        return False

    def insert_tabs(self, event=None):
        self.insert(LINESTART, ' ' * 4)
        return 'break'

    def remove_tabs(self, event=None):
        if self.get(*CURRLINE).startswith(' ' * 4):
            self.delete(LINESTART, LINESTART + '+4c')
        return 'break'

    def select_all(self, event=None):
        self.select()
        return 'break'

    def select(self, start, end):
        self.tag_add(Tk.SEL, start, end)

    def deselect_all(self, event=None):
        self.deselect()
        return 'break'

    def deselect(self, start=START, end=END):
        with ignored(Tk.TclError):
            self.tag_remove(Tk.SEL, start, end)

    def copy_text(self, event=None):
        with ignored(Tk.TclError):
            self._copy(SELECTION)
        return 'break'

    def _copy(self, borders=SELECTION, clip=True):
        '''@error: raise TclError if no text is selected'''
        text = '\x08' + json.dumps(self.formatted_get(*borders),
                                   ensure_ascii=False).replace('],', '],\n')
        if clip:
            self.clipboard_clear()
            self.clipboard_append(text)
        return text

    def cut_text(self, event=None):
        with ignored(Tk.TclError):
            self._cut(SELECTION)
        return 'break'

    def _cut(self, borders=SELECTION, clip=True):
        '''@error: raise TclError if no text is selected'''
        borders = borders or SELECTION
        self.delete(*borders)
        return self._copy(borders, clip)

    def paste_text(self, event=None):
        try:
            self._paste()
        except Tk.TclError:
            self._paste(borders=NO_SELECTION)
        self.deselect_all()
        return 'break'

    def _paste(self, location=INSERT, borders=SELECTION, text=''):
        '''@error: raise TclError if no text is selected'''
        self.delete(*borders)
        self.mark_set(INSERT, location)
        try:
            text = text or self.clipboard_get()
        except Tk.TclError:
            return
        if text.startswith('\x08'):
            tag = ''
            sel = ''
            tags = json.loads(text[1:])
            for key, value, index in tags:
                if key == 'mark' and value == INSERT:
                    self.mark_set(USER_MARK, INSERT)
                    self.mark_gravity(USER_MARK, Tk.LEFT)
                if key == 'tagon':
                    if value == Tk.SEL:
                        sel = Tk.SEL
                    else:
                        tag = value
                elif key == 'text':
                    self.insert(value, (tag, sel))
                elif key == 'tagoff':
                    if value == Tk.SEL:
                        sel = ''
                    else:
                        tag = ''
        else:
            self.insert(text)
        self.tag_remove('', *ALL)

    def delete_line(self, event=None):
        try:
            self.delete(*SEL_LINE)
        except Tk.TclError:
            self.delete(*CURRLINE)
        return 'break'

    def backspace_word(self, event):
        if self.get_char(INSERT + '-1c') in '.,;:?! ':
            correction = '-2c wordstart'
        elif self.get_char() in ' ':
            correction = '-1c wordstart -1c'
        else:
            correction = '-1c wordstart'
        self.delete(INSERT + correction, INSERT)
        return 'break'

    def delete_word(self, event):
        if (
            self.get_char(INSERT + '-1c') in ' .,;:?!\n' or
            self.compare(INSERT, '==', '1.0')
        ):
            correction = ' wordend +1c'
        elif get_char() == ' ':
            correction = '+1c wordend'
        elif get_char() in '.,;:?!':
            correction = '+1c'
        else:
            correction = ' wordend'
        self.delete(INSERT, INSERT + correction)
        return 'break'

    def move_line(self, event):
        self.insert('\n', END)  # ensures last line can be moved normally
        if self.compare(END, '==', INSERT):  # ensures last line can be...
            self.mark_set(INSERT, f'{END}-1c')  # ...moved from the last char.
        location = PREV_LINE if event.keysym == 'Up' else NEXT_LINE
        try:
            text = self._cut(SEL_LINE, False)
            self._paste(location, NO_SELECTION, text)
        except Tk.TclError:
            text = self._cut(CURRLINE, False)
            self._paste(location, NO_SELECTION, text)
        self.mark_set(INSERT, USER_MARK)
        self.delete(f'{END}-1c')  # removes helper newline
        return 'break'

    @property
    def commands(self):
        return [('<Control-MouseWheel>', self.change_fontsize),
                ('<Return>', self.indent),
                ('<KeyPress>', self.insert_characters),
                (('<Tab>', '<Control-]>'), self.insert_tabs),
                (('<Shift-Tab>', '<Control-[>'), self.remove_tabs),
                ('<Control-0>', self.reset_fontsize),
                ('<Control-a>', self.select_all),
                ('<Control-c>', self.copy_text),
                ('<Control-K>', self.delete_line),
                ('<Control-v>', self.paste_text),
                ('<Control-x>', self.cut_text),
                ('<Control-BackSpace>', self.backspace_word),
                ('<Control-Delete>', self.delete_word),
                (('<Control-Up>', '<Control-Down>'), self.move_line)]

    # @property
    def styles(self):
        return [
            Style(font='Calibri', size=18, group='default'),
            Style(name='example', key='F', tags=(
                '[f]', ''), lmargin1='2c', spacing1='5m', group='paragraph'),
            Style(name='example-no-lines', key='e',
                  tags=('[e]', ''), lmargin1='2c', group='paragraph'),
            Style(name='bold', key='b', tags=(
                 '<strong>', '</strong>'), bold=True),
            Style(name='italics', key='i', tags=(
                 '<em>', '</em>'), italics=True),
            Style(name='small-caps', key='k', tags=('<small-caps>', '</small-caps>'),
                        font='Alegreya SC'),
            Style(name='links', key='n', tags=('<link>', '</link>'), underline=True,
                        colour='blue'),
            Style(name='broken-links', tags=('<bink>', '</bink>'), underline=True,
                        colour='red'),
            Style(name='tinellbian', tags=('<high-lulani>', '</high-lulani>'),
                        font='Tinellbian'),
            Style(name='ipa', key='I', tags=('<ipa>', '</ipa>'),
                        font='Lucida Sans Unicode')]
