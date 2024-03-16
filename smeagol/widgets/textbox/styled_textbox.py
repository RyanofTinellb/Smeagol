import tkinter as tk
from smeagol.utilities import utils
from smeagol.widgets.textbox.base_textbox import BaseTextbox

from smeagol.conversion.text_tree.text_tree import TextTree


SELECTION = "sel.first", "sel.last"


class StyledTextbox(BaseTextbox):
    def __init__(self, parent=None, styles=None, languages=None):
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
        return TextTree(self.formatted_text)

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

    def get_styles(self, _event=None):
        if not self.styles:
            return
        self.styles.update(self.tag_names(tk.INSERT))

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
        if style.language:
            for language in self.languages:
                language = language[:2]
                self.tag_config(f"{name}-{language}", **style.paragraph)
        if key:
            self.bind(f"<Control-{key}>", self.style_changer(name, style))

    def style_changer(self, name, style):
        def command(_=None, name=name):
            if style.language and (code := self.language_code):
                name += f"-{code}"
            self.styles.toggle(name)
            return "break"

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
