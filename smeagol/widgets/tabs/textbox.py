import re
import json
import tkinter as tk
from smeagol.utilities import utils
from smeagol.conversion import api as conversion
from smeagol.widgets.api import Styles

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
NO_SELECTION = INSERT, INSERT
USER_MARK = 'usermark'

BRACKETS = {'[': ']', '<': '>', '{': '}', '"': '"', '(': ')'}


class Textbox(tk.Text):
    def __init__(self, parent=None):
        super().__init__(parent, height=1, width=1, wrap=tk.WORD,
                         undo=True)
        self.displays = dict(wordcount=tk.StringVar(), randomwords=tk.StringVar(),
                         style=tk.StringVar(), language=tk.StringVar())
        self.add_commands()
    
    @property
    def translator(self):
        return self._translator
    
    @translator.setter
    def translator(self, translator):
        self._translator = translator
        self.languages = translator.languages
        self.language.set(translator.fullname)
    
    @property
    def styles(self):
        with utils.ignored(AttributeError):
            return self._styles
    
    @styles.setter
    def styles(self, styles):
        self._styles = styles
        self.set_styles()

    def grid(self, *args, **kwargs):
        super().grid(*args, **kwargs)
        return self

    def __getattr__(self, attr):
        match attr:
            case 'text':
                return self.get()
            case 'current_style':
                return self.style.get().split()
            case 'language_code':
                if language := self.language.get():
                    return language[:2]
            case 'font':
                return self.styles['default'].create_font()
            case default:
                try:
                    return self.displays[attr]
                except KeyError:
                    return getattr(super(), attr)

    def __setattr__(self, attr, value):
        match attr:
            case 'text':
                return self._paste(borders=ALL, text=value)
            case 'current_style':
                with utils.ignored(AttributeError):
                    value = '\n'.join([v for v in value if v != 'sel'])
                self.style.set(value)
        super().__setattr__(attr, value)

    def clear_style(self, styles):
        self.tag_remove(styles, tk.INSERT)

    def set_styles(self):
        if self.styles is None:
            return
        self.current_style = ''
        with utils.ignored(KeyError):
            self.set_default_style()
        for style in self.styles:
            self._set_style(style)

    def set_default_style(self):
        if (default := self.styles.default):
            self.config(**default.textbox_settings)

    def _set_style(self, style):
        name = style.name
        key = style.key
        self.tag_config(name, **style.paragraph)
        if style.language:
            for language in self.languages:
                language = language[:2]
                self.tag_config(f'{name}-{language}', **style.paragraph)
        if key:
            self.bind(f'<Control-{key}>', self.style_changer(name, style))

    def style_changer(self, name, style):
        def command(event, name=name):
            if style.language and (code := self.language_code):
                name += f'-{code}'
            self._change_style(name)
            return 'break'
        return command

    def _change_style(self, name):
        styles = set(self.current_style)
        if name in self.current_style:
            self._remove_style(name, styles)
        else:
            self._add_style(name, styles)
        self.current_style = styles

    def _add_style(self, name, styles):
        styles.add(name)
        with utils.ignored(tk.TclError):
            self.tag_add(name, *SELECTION)

    def _remove_style(self, name, styles):
        styles.discard(name)
        with utils.ignored(tk.TclError):
            self.tag_remove(name, *SELECTION)

    def update_styles(self):
        self.set_styles()
        self.add_commands()

    def add_commands(self):
        for keys, command in self.commands:
            if isinstance(keys, str):
                self.bind(keys, command)
            else:
                for key in keys:
                    self.bind(key, command)

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
        self.current_style = ''

    def replace(self, text, start=START, end=END):
        self.delete(start, end)
        self.insert(text, start)

    def insert(self, text='', position=INSERT, tags=None):
        super().insert(position, text, tags)

    def delete(self, start=START, end=END):
        super().delete(start, end)

    def clear(self):
        self.delete()

    def key_released(self, event):
        self.update_wordcount()
        if event.keycode == '??' or 33 <= event.keycode <= 40:
            self.current_style = self.tag_names(tk.INSERT)

    def update_wordcount(self):
        text = self.text
        wordcount = text.count(' ') + text.count('\n') - text.count('|')
        self.displays['wordcount'].set(wordcount)

    def modify_fontsize(self, size):
        self.font.config(size=size)
        self.config(font=self.font)
        for (name, _, style) in self.styles:
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

    def move_mark(self, mark, dist):
        sign = '+' if dist >= 0 else '-'
        dist = abs(dist)
        self.mark_set(INSERT, mark)
        self.mark_set(mark, f'{mark}{sign}{dist}c')

    def insert_characters(self, event):
        key = event.char
        keysym = event.keysym
        # code = event.keycode
        styles = self.current_style
        if keysym.startswith('Control_'):
            self.edit_modified(False)
        elif keysym == 'BackSpace':
            return
        elif key and event.num == '??':
            if not self.match_brackets(key):
                try:
                    self.delete(*SELECTION)
                    self.insert(key, tk.SEL, tags=styles)
                except tk.TclError:
                    self.insert(key, tags=styles)
            return 'break'
        elif keysym == 'Return':
            spaces = re.sub(r'( *).*', r'\1', self.get(*CURRLINE))
            self.insert(spaces, INSERT)
            return 'break'

    def match_brackets(self, key):
        if key in BRACKETS:
            try:
                self.insert(key, tk.SEL_FIRST, tags=self.current_style)
                self.insert(BRACKETS[key], tk.SEL_LAST,
                            tags=self.current_style)
            except tk.TclError:
                self.insert(key + BRACKETS[key], tags=self.current_style)
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

    def select(self, start='1.0', end='end'):
        self.tag_add(tk.SEL, start, end)

    def deselect_all(self, event=None):
        self.deselect()
        return 'break'

    def deselect(self, start=START, end=END):
        with utils.ignored(tk.TclError):
            self.tag_remove(tk.SEL, start, end)

    def copy_text(self, event=None):
        with utils.ignored(tk.TclError):
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
        with utils.ignored(tk.TclError):
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
        except tk.TclError:
            self._paste(borders=NO_SELECTION)
        self.deselect_all()
        return 'break'

    def _paste(self, location=INSERT, borders=SELECTION, text=None):
        '''@error: raise TclError if no text is selected'''
        self.delete(*borders)
        self.mark_set(INSERT, location)
        try:
            text = text if text is not None else self.clipboard_get()
        except tk.TclError:
            return
        styles = []
        if type(text) != list:
            if not text.startswith('\x08'):
                self.insert(text)
                return
            text = json.loads(text[1:])
        for elt in text:
            finished = self._insert(styles, *elt)
            if finished:
                break

    def _insert(self, styles, key, value, index=0):
        match key:
            case 'mark':
                if value == INSERT:
                    self.mark_set(USER_MARK, INSERT)
                    self.mark_gravity(USER_MARK, tk.LEFT)
            case 'tagon':
                styles.append(value)
            case 'text':
                self.insert(value, tags=styles)
            case 'tagoff':
                try:
                    styles.remove(value)
                except ValueError:
                    print(f"Unable to find closing tag for <{styles.pop()}>")
                    return True

    def delete_line(self, event=None):
        try:
            self.delete(*SEL_LINE)
        except tk.TclError:
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
        elif self.get_char() == ' ':
            correction = '+1c wordend'
        elif self.get_char() in '.,;:?!':
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
        except tk.TclError:
            text = self._cut(CURRLINE, False)
            self._paste(location, NO_SELECTION, text)
        self.mark_set(INSERT, USER_MARK)
        self.delete(f'{END}-1c')  # removes helper newline
        return 'break'

    @property
    def commands(self):
        return [('<Control-MouseWheel>', self.change_fontsize),
                ('<Return>', self.indent),
                # ('<KeyPress>', self.insert_characters),
                (('<KeyRelease>', '<ButtonRelease>'), self.key_released),
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
