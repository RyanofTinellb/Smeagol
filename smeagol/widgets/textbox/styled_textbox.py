import tkinter as tk
from smeagol.utilities import utils
from smeagol.widgets.textbox.base_textbox import BaseTextbox
from smeagol.utilities.types import Styles, Style

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
        self.default_ime = {}
        self.ime = {}
        self.off_keys = {}
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

    def get_styles_from_cursor(self, event=None):
        offset = '' if event and event.keysym == 'h' else '-1c'
        override = event and event.keysym in 'hg'
        self._get_styles_from_cursor(offset, override)
        return 'break'

    def _get_styles_from_cursor(self, offset='', override: bool = False):
        mark = 'sel.last' if self.tag_ranges('sel') else tk.INSERT
        if not self.styles:
            return
        self.configure_tags()
        tags = self._get_tags(mark, offset, override)
        self.ime = self.invoke_ime(tags)
        self.styles.update(tags, self.styles_menu)
        self.update_displays()

    def _get_tags(self, mark, offset, override: bool):
        if override or not self.index(mark).endswith('.0'):
            return self.tag_names(mark + offset)
        tags = self.tag_names(mark)
        return list(filter(lambda tag: self.styles[tag].block, tags))

    def invoke_ime(self, tags):
        tags = list(filter(lambda tag: self.styles[tag].ime, tags))
        if not tags:
            return self.default_ime
        tag = self.styles[tags[0]]
        self._invoke_ime(tag)
        return self._invoke_ime(tag)

    def _invoke_ime(self, style: Style, activated: bool = True):
        if not (style and activated):
            return self.default_ime
        code = self.styles.language_code if style.language else ''
        ime = self.styles.imes.get(style.ime, {}).get(code, {})
        return ime

    def update_style_display(self):
        current = map(self._add_symbols, style_names(
            self.styles.current)) if self.styles else ''
        self.style.set('\n'.join(current))
        self.language_code.set(self.styles.language_code)

    def _add_symbols(self, tag):
        tag += '*' if self.styles[tag].ime else ''
        tag += '†' if self.styles[tag].language else ''
        return tag

    def clear_styles_menu(self):
        self.styles.clear(self.styles_menu)

    def configure_tags(self, menu=None):
        if self.styles is None:
            return
        with utils.ignored(KeyError):
            self._configure_default_style()
        if menu:
            menu.delete(0, menu.index('end'))
        self.off_keys.clear()
        for style in self.styles:
            self._configure_tag(style)
            var = self.styles_menu.setdefault(style.name, tk.IntVar())
            self._configure_styles_menu(menu, style, var)

    def _configure_styles_menu(self, menu, style, var):
        if not menu:
            return
        key = ('ctrl+' + style.key if style.key else '').replace('KeyPress-', ''
                                                                 ).replace('Alt-', 'alt+')
        menu.add_checkbutton(label=style.name + 10 * ' ' + key,
                             variable=var,
                             command=self.style_changer(style))

    def _configure_default_style(self):
        if not self.styles:
            return
        if (default := self.styles['default']):
            self.config(**default.textbox_settings)
            self.default_ime = self.styles.imes.get(default.ime, {})

    def _configure_tag(self, style):
        self.tag_config(style.name, **style.paragraph)
        if style.language:
            self._configure_language_tags(style)
        if (key := style.key):
            self.bind(f'<Control-{key}>', self.style_changer(style))
        if (off_key := style.off_key):
            self.off_keys.setdefault(off_key, []).append(
                self.style_deactivater(style))

    def _configure_language_tags(self, style):
        for code in self.languages:
            self.tag_config(f'{style.name}@{code}', **style.paragraph)

    def style_changer(self, style: Style):
        def command(_event=None, style=style):
            name = style.name
            language = style.language
            code = self.styles.language_code if language else ''
            at = '@' if code else ''
            name = f'{name}{at}{code}'
            on = self.styles.toggle(name)
            self.ime = self._invoke_ime(style, on)
            with utils.ignored(tk.TclError):
                (self.tag_add if self.styles.on(name)
                 else self.tag_remove)(name, *SELECTION)
            self.update_displays()
            return 'break'
        return command

    def _deactivate_styles(self, key):
        for command in self.off_keys.get(f'{key}', []):
            command()

    def style_deactivater(self, style: Style):
        def command(_event=None, style=style):
            name = style.name
            language = style.language
            code = self.styles.language_code if language else ''
            at = '@' if code else ''
            name = f'{name}{at}{code}'
            self.styles.deactivate(name)
            self._invoke_ime(style, False)
            with utils.ignored(tk.TclError):
                (self.tag_remove)(name, *SELECTION)
            self.update_displays()
        return command

    def _add_style(self, name):
        self.styles.activate(name)
        with utils.ignored(tk.TclError):
            self.tag_add(name, *SELECTION)

    def _remove_style(self, name):
        self.styles.deactivate(name)
        with utils.ignored(tk.TclError):
            self.tag_remove(name, *SELECTION)
