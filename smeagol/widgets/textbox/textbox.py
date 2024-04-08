import re
import tkinter as tk

from smeagol.widgets.textbox.clipboard_textbox import ClipboardTextbox

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

BRACKETS = {'[': ']', '<': '>', '{': '}', '"': '"', '(': ')', '‘': '’', '“': '”'}


class Textbox(ClipboardTextbox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.displays.update({
            'wordcount': tk.IntVar()})
        self.add_commands(self.commands)

    @property
    def translator(self):
        return self._translator

    @translator.setter
    def translator(self, translator):
        self._translator = translator
        self.languages = translator.languages
        self.language.set(translator.fullname)

    def __getattr__(self, attr):
        match attr:
            case 'plaintext':
                return self.read()
            case 'language_code':
                if language := self.language.get():
                    return language[:2]
            case _:
                try:
                    return self.displays[attr]
                except KeyError:
                    return getattr(super(), attr)

    def __setattr__(self, attr, value):
        match attr:
            case 'text':
                self.reset()
                self._paste(borders=ALL, text=value)
                self.update()
            case _default:
                super().__setattr__(attr, value)

    def add_commands(self, commands):
        for keys, command in commands:
            if isinstance(keys, str):
                self.bind(keys, command)
            else:
                for key in keys:
                    self.bind(key, command)

    def reset(self):
        self.edit_modified(False)
        self.styles.clear()

    def update(self):
        self.update_wordcount()
        self.update_style()

    def _key_released(self, event=None):
        if (event.keysym in ['Prior', 'Next', 'Left', 'Right', 'Down', 'Up', 'Home', 'End'] or
                int(event.type) == 5):
            self.get_styles()
        self.update_wordcount()
        self.update_style()

    def update_wordcount(self):
        text = self.plaintext
        wordcount = text.count(' ') + text.count('\n') - text.count('|')
        self.displays['wordcount'].set(wordcount)

    def indent(self, _event=None):
        spaces = re.match(r'^ *', self.get(*CURRLINE)).group(0)
        self.write('\n' + spaces)
        return 'break'

    def move_mark(self, mark, dist):
        sign = '+' if dist >= 0 else ''
        self.mark_set(INSERT, mark)
        self.mark_set(mark, f'{mark}{sign}{dist}c')

    def insert_characters(self, event):
        key = event.char
        keysym = event.keysym
        # code = event.keycode
        if keysym.startswith('Control_'):
            self.edit_modified(False)
        elif keysym == 'BackSpace':
            return None
        elif key and event.num == '??':
            if not self.match_brackets(key):
                try:
                    self.delete(*SELECTION)
                    self.write(key, tk.SEL)
                except tk.TclError:
                    self.write(key)
            return 'break'
        elif keysym == 'Return':
            spaces = re.sub(r'( *).*', r'\1', self.get(*CURRLINE))
            self.insert(spaces, INSERT)
            return 'break'
        return None

    def match_brackets(self, key):
        if key in BRACKETS:
            try:
                self.write(key, tk.SEL_FIRST)
                self.write(BRACKETS[key], tk.SEL_LAST)
            except tk.TclError:
                self.write(key + BRACKETS[key])
                self.move_mark(INSERT, -1)
            return True
        return False

    def insert_tabs(self, _event=None):
        self.write(LINESTART, ' ' * 4)
        return 'break'

    def remove_tabs(self, _event=None):
        if self.get(*CURRLINE).startswith(' ' * 4):
            self.remove(LINESTART, LINESTART + '+4c')
        return 'break'

    def delete_line(self, _=None):
        try:
            self.delete(*SEL_LINE)
        except tk.TclError:
            self.delete(*CURRLINE)
        return 'break'

    def backspace_word(self, _):
        if self.get_char(INSERT + '-1c') in '.,;:?! ':
            correction = '-2c wordstart'
        elif self.get_char() in ' ':
            correction = '-1c wordstart -1c'
        else:
            correction = '-1c wordstart'
        self.delete(INSERT + correction, INSERT)
        return 'break'

    def delete_word(self, _):
        if self.get_char(INSERT + '-1c') in ' .,;:?!\n' or self.compare(
            INSERT, '==', '1.0'
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
        return [
            ('<Control-MouseWheel>', self.modify_fontsize),
            ('<Return>', self.indent),
            ('<KeyPress>', self.insert_characters),
            (('<KeyRelease>', '<ButtonRelease>'), self._key_released),
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
            (('<Control-Up>', '<Control-Down>'), self.move_line)
        ]
