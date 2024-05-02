import tkinter as tk
from smeagol.utilities import utils
from smeagol.widgets.textbox.base_textbox import BaseTextbox
from smeagol.utilities.types import Styles

from smeagol.conversion.text_tree.text_tree import TextTree


SELECTION = "sel.first", "sel.last"


def style_names(styles: list[str]):
    return [style_name(style) for style in styles]


def style_name(style: str):
    if style and '@' in style:
        style, _language = style.split('@')
    return style


class StyledTextbox(BaseTextbox):
    def __init__(self, parent=None, styles: Styles = None, languages: dict = None):
        super().__init__(parent, height=1, width=1, wrap=tk.WORD, undo=True)
        self.styles = styles
        self.styles_menu: dict[str, tk.IntVar] = {}
        self.languages = languages or {}
        self.displays = {'style': tk.StringVar(),
                         'language_code': tk.StringVar()}

    def __getattr__(self, attr):
        match attr:
            case 'font':
                return self.styles['default'].create_font()
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
        self.configure_tags()
        return 'break'

    def _modify_fontsize(self, amount):
        self.styles.modify_fontsize(amount)

    def reset_fontsize(self, _event=None):
        self.styles.reset_fontsize()
        self.configure_tags()
        return 'break'

    def get_styles_from_cursor(self, _event=None):
        if not self.styles:
            return
        self.configure_tags()
        self.styles.update(self.tag_names(tk.INSERT + '-1c'), self.styles_menu)

    def update_style_display(self):
        current = style_names(self.styles.current) if self.styles else ''
        self.style.set('\n'.join(current))
        self.language_code.set(self.styles.language_code)

    def configure_tags(self, menu=None):
        if self.styles is None:
            return
        with utils.ignored(KeyError):
            self._configure_default_style()
        if menu:
            menu.delete(0, menu.index('end'))
        for style in self.styles:
            self._configure_tag(style)
            var = self.styles_menu.setdefault(style.name, tk.IntVar())
            self._configure_styles_menu(menu, style, var)

    def _configure_styles_menu(self, menu, style, var):
        if not menu:
            return
        menu.add_checkbutton(label=style.name,
                             variable=var,
                             command=self.style_changer(style.name, style.language))

    def _configure_default_style(self):
        if not self.styles:
            return
        if default := self.styles['default']:
            self.config(**default.textbox_settings)

    def _configure_tag(self, style):
        self.tag_config(style.name, **style.paragraph)
        if style.language:
            self._configure_language_tags(style)
        if (key := style.key):
            self.bind(f'<Control-{key}>',
                      self.style_changer(style.name, style.language))

    def _configure_language_tags(self, style):
        for code in self.languages:
            self.tag_config(f'{style.name}@{code}', **style.paragraph)

    def style_changer(self, name: str, language: bool):
        def command(_event=None, name=name, language=language):
            # self.focus_set()
            code = f'@{self.styles.language_code}' if language else ''
            name = f'{name}{code}'
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
