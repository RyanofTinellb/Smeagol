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


class Textbox(ClipboardTextbox):
    def __init__(self, clipboard, parent=None):
        super().__init__(clipboard, parent)
        self.parent = parent
        self.displays.update({
            'wordcount': tk.IntVar(),
            'title': tk.StringVar()})
        self.add_commands(self.commands)
        self._history = ''

    def __getattr__(self, attr):
        match attr:
            case 'plaintext':
                return self.read()
            case 'title':
                return self.displays[attr].get()
            case _other:
                try:
                    return self.displays[attr]
                except KeyError:
                    return super().__getattr__(attr)

    def __setattr__(self, attr, value):
        match attr:
            case 'text':
                self.reset()
                self._paste(borders=ALL, text=value)
                self.update_displays()
            case 'title':
                self.displays[attr].set(value)
            case _default:
                super().__setattr__(attr, value)

    def reset(self):
        self.edit_modified(False)
        self.styles.clear()

    def update_displays(self):
        self.update_wordcount()
        self.update_style_display()

    @property
    def _cursor_buttons(self):
        return ['Prior', 'Next', 'Left', 'Right', 'Down', 'Up', 'Home', 'End']

    def _key_released(self, event):
        if (event.keysym in self._cursor_buttons or
                event.type == tk.EventType.ButtonRelease):
            self._history = ''
            self.get_styles_from_cursor(event)
            return
        self.update_displays()

    def input_method_editor(self, key):
        self._history = self._history + key
        for word, replacement in self.ime.items():
            if self._history.endswith(word):
                self._history = self._history.removesuffix(word) + replacement
                self.overwrite_at_cursor(word, replacement)
                return
        self.write(key)

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
            return None
        if keysym.startswith('Alt_'):
            return None
        if keysym == 'BackSpace':
            self._history = self._history[:-1]
            self.get_styles_from_cursor(event)
            self.parent.show_edited()
            return None
        if keysym == 'space':
            if not (event.state & 4): # CTRL key
                self._deactivate_styles('space')
            self.input_method_editor(key)
            self.parent.show_edited()
            return 'break'
        if keysym == 'Return':
            self._deactivate_styles('Return')
            self._deactivate_styles('space')
            self.write('\n')
            return 'break'
        if key and event.num == '??':
            try:
                self.delete(*SELECTION)
                self.write(key, tk.SEL)
            except tk.TclError:
                self.input_method_editor(key)
            return 'break'
        return None

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

    @property
    def commands(self):
        return [
            ('<Control-MouseWheel>', self.modify_fontsize),
            # ('<Return>', self.indent),
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
            (('<Alt-g>', '<Alt-h>'), self.get_styles_from_cursor)
        ]
