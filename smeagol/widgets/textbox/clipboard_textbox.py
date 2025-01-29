from typing import Optional
import tkinter as tk
import json
from smeagol.utilities.types import TextTree, Node
from smeagol.utilities import utils
from smeagol.widgets.textbox.styled_textbox import StyledTextbox

INSERT = "insert"
SELECTION = "sel.first", "sel.last"
NO_SELECTION = INSERT, INSERT
START = "1.0"
END = "end-1c"
USER_MARK = "usermark"


class ClipboardTextbox(StyledTextbox):

    def overwrite(self, text, start=START, end=END):
        self.delete(start, end)
        self.write(text, start)

    def overwrite_at_cursor(self, word, replacement):
        self.delete(f'{INSERT}-{len(word)-1}c', INSERT)
        self.write(replacement)

    def write(self, text="", position=INSERT, tags: Optional[list] = None):
        current = self.styles.current if self.styles else ''
        tags = tags or current
        text = text.replace('&lt;', '<').replace('&gt;', '>')
        super().insert(position, text, tags)

    def remove(self, start=START, end=END):
        super().delete(start, end)

    def clear(self):
        self.remove()

    def select_all(self, _event=None):
        self.select()
        return "break"

    def select(self, start="1.0", end="end"):
        self.tag_add(tk.SEL, start, end)

    def deselect_all(self, _event=None):
        self.deselect()
        return "break"

    def deselect(self, start=START, end=END):
        with utils.ignored(tk.TclError):
            self.tag_remove(tk.SEL, start, end)

    def copy_text(self, _event=None):
        with utils.ignored(tk.TclError):
            self._copy()
        return "break"

    def _copy(self, borders=SELECTION, clip=True):
        """@error: raise TclError if no text is selected"""
        text = "\x08" + json.dumps(
            self.formatted_get(*borders), ensure_ascii=False
        ).replace("],", "],\n")
        if clip:
            self.clipboard_clear()
            self.clipboard_append(text)
        return text

    def cut_text(self, _event=None):
        with utils.ignored(tk.TclError):
            self._copy()
            self._cut()
        return "break"

    def _cut(self, borders=SELECTION, clip=True):
        """@error: raise TclError if no text is selected"""
        borders = borders or SELECTION
        self.delete(*borders)
        return self._copy(borders, clip)

    def paste_text(self, _event=None):
        try:
            self._paste()
        except tk.TclError:
            self._paste(borders=NO_SELECTION)
        self.deselect_all()
        return "break"

    def _paste(self, location=INSERT, borders=SELECTION, text=None):
        """@error: raise TclError if no text is selected"""

        # """
        # Possible things to PASTE:
        #     unformatted string
        #     json object (tkinter text dump)
        #     stringified json object (tkinter text dump with leading \x08)
        #     text tree

        # Possible origins:
        #     passed in argument
        #     clipboard
        # """
        self.delete(*borders)
        self.mark_set(INSERT, location)
        try:
            text = text if text is not None else self.clipboard_get()
        except tk.TclError:
            return
        if not isinstance(text, list):
            self._insert_string(text)

    def _insert_tuples(self, text):
        for elt in text:
            finished = self._insert(*elt)
            if finished:
                break

    def _insert_string(self, text):
        try:
            if not text.startswith("\x08"):
                self.write(text)
                return
        except AttributeError:
            self._insert_tree(text)
            return
        text = json.loads(text[1:])
        self._insert_tuples(text)

    def _insert_tree(self, tree: TextTree | Node):
        for leaf in tree:
            self._insert_leaf(leaf)

    def _insert_leaf(self, leaf: str | Node):
        try:
            self.styles.activate(leaf.name)
            self._insert_children(leaf.children)
            self.styles.deactivate(leaf.name)
        except AttributeError:
            self.write(leaf)

    def _insert_children(self, children):
        for child in children:
            self._insert_leaf(child)

    def _insert(self, key, value, _=0):
        match key:
            case "mark":
                if value == INSERT:
                    self.mark_set(USER_MARK, INSERT)
                    self.mark_gravity(USER_MARK, tk.LEFT)
            case "tagon":
                self.styles.activate(value)
            case "text":
                self.write(value)
            case "tagoff":
                try:
                    self.styles.deactivate(value)
                except ValueError as e:
                    raise ValueError(f"Unable to find closing tag for <{
                                     self.styles.current.final}>") from e
        return False
