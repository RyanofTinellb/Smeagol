import re
import tkinter as tk

from smeagol.utilities import utils
from smeagol.widgets.textbox.clipboard_textbox import ClipboardTextbox

START = "1.0"
END = "end-1c"
ALL = START, END
INSERT = "insert"
LINESTART = "insert linestart"
LINEEND = "insert lineend+1c"
CURRLINE = LINESTART, LINEEND
PREV_LINE = "insert linestart -1l"
PREVLINE = f"{PREV_LINE} lineend"
NEXT_LINE = "insert linestart +1l"
SELECTION = "sel.first", "sel.last"
SEL_LINE = "sel.first linestart", "sel.last lineend+1c"
NO_SELECTION = INSERT, INSERT
USER_MARK = "usermark"

BRACKETS = {"[": "]", "<": ">", "{": "}", '"': '"', "(": ")"}


class Textbox(ClipboardTextbox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.displays.update({
            "style": tk.StringVar(),
            "language": tk.StringVar()})

    @property
    def translator(self):
        return self._translator

    @translator.setter
    def translator(self, translator):
        self._translator = translator
        self.languages = translator.languages
        self.language.set(translator.fullname)

    def grid(self, *args, **kwargs):
        super().grid(*args, **kwargs)
        return self

    def __getattr__(self, attr):
        match attr:
            case "text":
                return self.read()
            case "language_code":
                if language := self.language.get():
                    return language[:2]
            case "font":
                return self.styles["default"].create_font()
            case _:
                try:
                    return self.displays[attr]
                except KeyError:
                    return getattr(super(), attr)

    def __setattr__(self, attr, value):
        match attr:
            case "text":
                return self._paste(borders=ALL, text=value)
        super().__setattr__(attr, value)

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

    def read(self, start=START, end=END):
        return super().get(start, end)

    def get_char(self, position=INSERT):
        return super().get(position)

    def formatted_get(self, start=START, end=END):
        return super().dump(start, end)

    def reset(self):
        self.edit_modified(False)
        self.styles.current = ""

    def overwrite(self, text, start=START, end=END):
        self.delete(start, end)
        self.write(text, start)

    def write(self, text="", position=INSERT, tags=None):
        tags = tags or self.styles.active_tags
        super().insert(position, text, tags)

    def remove(self, start=START, end=END):
        super().delete(start, end)

    def clear(self):
        self.remove()

    def key_released(self, _):
        self.update_wordcount()

    def update_wordcount(self):
        text = self.text
        wordcount = text.count(" ") + text.count("\n") - text.count("|")
        self.displays["wordcount"].set(wordcount)

    def modify_fontsize(self, size):
        self.font.config(size=size)
        self.config(font=self.font)
        for name, _, style in self.styles:
            self.tag_config(name, **style)

    def change_fontsize(self, event):
        sign = 1 if event.delta > 0 else -1
        size = self.font.actual(option="size") + sign
        self.modify_fontsize(size)
        return "break"

    def reset_fontsize(self, _event=None):
        self.modify_fontsize(18)
        return "break"

    def indent(self, _event=None):
        spaces = re.match(r"^ *", self.get(*CURRLINE)).group(0)
        self.write("\n" + spaces)
        return "break"

    def move_mark(self, mark, dist):
        sign = "+" if dist >= 0 else "-"
        dist = abs(dist)
        self.mark_set(INSERT, mark)
        self.mark_set(mark, f"{mark}{sign}{dist}c")

    def insert_characters(self, event):
        key = event.char
        keysym = event.keysym
        # code = event.keycode
        if keysym.startswith("Control_"):
            self.edit_modified(False)
        elif keysym == "BackSpace":
            return None
        elif key and event.num == "??":
            if not self.match_brackets(key):
                try:
                    self.delete(*SELECTION)
                    self.write(key, tk.SEL)
                except tk.TclError:
                    self.write(key)
            return "break"
        elif keysym == "Return":
            spaces = re.sub(r"( *).*", r"\1", self.get(*CURRLINE))
            self.insert(spaces, INSERT)
            return "break"

    def match_brackets(self, key):
        if key in BRACKETS:
            try:
                self.write(key, tk.SEL_FIRST, tags=self.current_style)
                self.write(BRACKETS[key], tk.SEL_LAST, tags=self.current_style)
            except tk.TclError:
                self.write(key + BRACKETS[key], tags=self.current_style)
                self.move_mark(INSERT, -1)
            return True
        return False

    def insert_tabs(self, _event=None):
        self.write(LINESTART, " " * 4)
        return "break"

    def remove_tabs(self, _event=None):
        if self.get(*CURRLINE).startswith(" " * 4):
            self.remove(LINESTART, LINESTART + "+4c")
        return "break"

    def delete_line(self, _=None):
        try:
            self.delete(*SEL_LINE)
        except tk.TclError:
            self.delete(*CURRLINE)
        return "break"

    def backspace_word(self, _):
        if self.get_char(INSERT + "-1c") in ".,;:?! ":
            correction = "-2c wordstart"
        elif self.get_char() in " ":
            correction = "-1c wordstart -1c"
        else:
            correction = "-1c wordstart"
        self.delete(INSERT + correction, INSERT)
        return "break"

    def delete_word(self, _):
        if self.get_char(INSERT + "-1c") in " .,;:?!\n" or self.compare(
            INSERT, "==", "1.0"
        ):
            correction = " wordend +1c"
        elif self.get_char() == " ":
            correction = "+1c wordend"
        elif self.get_char() in ".,;:?!":
            correction = "+1c"
        else:
            correction = " wordend"
        self.delete(INSERT, INSERT + correction)
        return "break"

    def move_line(self, event):
        self.insert("\n", END)  # ensures last line can be moved normally
        if self.compare(END, "==", INSERT):  # ensures last line can be...
            self.mark_set(INSERT, f"{END}-1c")  # ...moved from the last char.
        location = PREV_LINE if event.keysym == "Up" else NEXT_LINE
        try:
            text = self._cut(SEL_LINE, False)
            self._paste(location, NO_SELECTION, text)
        except tk.TclError:
            text = self._cut(CURRLINE, False)
            self._paste(location, NO_SELECTION, text)
        self.mark_set(INSERT, USER_MARK)
        self.delete(f"{END}-1c")  # removes helper newline
        return "break"

    @property
    def commands(self):
        return [
            ("<Control-MouseWheel>", self.change_fontsize),
            ("<Return>", self.indent),
            # ('<KeyPress>', self.insert_characters),
            (("<KeyRelease>", "<ButtonRelease>"), self.key_released),
            (("<Tab>", "<Control-]>"), self.insert_tabs),
            (("<Shift-Tab>", "<Control-[>"), self.remove_tabs),
            ("<Control-0>", self.reset_fontsize),
            ("<Control-a>", self.select_all),
            ("<Control-c>", self.copy_text),
            ("<Control-K>", self.delete_line),
            ("<Control-v>", self.paste_text),
            ("<Control-x>", self.cut_text),
            ("<Control-BackSpace>", self.backspace_word),
            ("<Control-Delete>", self.delete_word),
            (("<Control-Up>", "<Control-Down>"), self.move_line),
        ]
