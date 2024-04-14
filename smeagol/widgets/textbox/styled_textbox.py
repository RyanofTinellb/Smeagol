import tkinter as tk
from smeagol.utilities import utils
from smeagol.widgets.textbox.base_textbox import BaseTextbox
from smeagol.utilities.types import Styles

from smeagol.conversion.text_tree.text_tree import TextTree


SELECTION = "sel.first", "sel.last"


class StyledTextbox(BaseTextbox):
    def __init__(self, parent=None, styles: Styles =None, languages=None):
        super().__init__(parent, height=1, width=1, wrap=tk.WORD, undo=True)
        self.styles = styles
        self.languages = languages or {}
        self.displays = {"style": tk.StringVar(),
                         "language": tk.StringVar()}

    def __getattr__(self, attr):
        match attr:
            case "language_code":
                if language := self.language.get():
                    return language[:2]
            case "font":
                return self.styles["default"].create_font()
            case _default:
                try:
                    return self.displays[attr]
                except KeyError:
                    return getattr(super(), attr)

    @property
    def text(self):
        return TextTree(self.formatted_text, self.styles.ranks)

    def modify_fontsize(self, event):
        sign = 1 if event.delta > 0 else -1
        self._modify_fontsize(sign)
        self.set_styles()
        return "break"

    def _modify_fontsize(self, amount):
        self.styles.modify_fontsize(amount)

    def reset_fontsize(self, _event=None):
        self.styles.reset_fontsize()
        self.set_styles()
        return "break"

    def get_styles(self, _event=None):
        if not self.styles:
            return
        self.styles.update(self.tag_names(tk.INSERT))
        self.update_styles()

    def update_style(self):
        current = self.styles.current if self.styles else ''
        self.style.set('\n'.join(current))

    def clear_style(self, styles):
        self.tag_remove(styles, tk.INSERT)

    def set_styles(self):
        if self.styles is None:
            return
        with utils.ignored(KeyError):
            self.set_default_style()
        for style in self.styles:
            self._set_style(style)

    def set_default_style(self):
        if not self.styles:
            return
        if default := self.styles['default']:
            self.config(**default.textbox_settings)

    def _set_style(self, style):
        name = style.name
        key = style.key
        self.tag_config(name, **style.paragraph)
        if key:
            self.bind(f'<Control-{key}>', self.style_changer(name))

    def style_changer(self, name):
        def command(_=None, name=name):
            self.styles.toggle(name)
            with utils.ignored(tk.TclError):
                (self.tag_add if self.styles.on(name)
                 else self.tag_remove)(name, *SELECTION)
            return 'break'
        return command

    def _add_style(self, name):
        self.styles.activate(name)
        with utils.ignored(tk.TclError):
            self.tag_add(name, *SELECTION)

    def _remove_style(self, name):
        self.styles.deactivate(name)
        with utils.ignored(tk.TclError):
            self.tag_remove(name, *SELECTION)

    def update_styles(self):
        self.set_styles()
        # self.add_commands()
