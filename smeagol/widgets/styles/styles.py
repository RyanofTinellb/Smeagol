import tkinter as tk

from smeagol.utilities import utils
from smeagol.widgets.styles.style import Style


class Styles:
    def __init__(self, styles):
        self.default = None
        self.language_code = None
        self._current = set()
        self.styles = {name: self.create_style(name, style)
                       for name, style in styles.items()}
        self.ranks = {name: style.rank for name, style in self.styles.items()}

    @property
    def current(self):
        return list(self._current)

    def create_style(self, name='', style=None):
        style = style or {}
        if self.default:
            return Style(name, style, default_style=self.default)
        # if style.get('tags', {}).get('type') == 'default':
        self.default = Style(name, style)
        return self.default

    def __contains__(self, item):
        return item in self.styles

    def __iter__(self):
        return iter(sorted(self.styles.values(), key=lambda s: s.name))

    def __getitem__(self, name):
        name, language = utils.try_split(name, '@', '')
        try:
            style = self.styles[name]
        except KeyError:
            self.styles[name] = Style(name, default_style=self.default)
            style = self.styles[name]
        style.language_code = language
        return style

    def __setitem__(self, name, value):
        self.styles[name] = value

    def __getattr__(self, attr):
        match attr:
            case 'copy':
                value = type(self)(self)
            case 'names':
                value = list(self.keys())
            case 'keys':
                value = self.styles.keys
            case 'values':
                value = self._items.values
            case 'items':
                value = self._items.items
            case '_items':
                value = {n: s.style for n, s in self.styles.items()}
            case _not_found:
                try:
                    return super().__getattr__(attr)
                except AttributeError as e:
                    raise AttributeError(
                        f'{type(self).__name__} object has no attribute {attr}') from e
        return value

    def add(self, style):
        ''' used by styles editor '''
        try:
            self.styles.setdefault(style.name, style)
        except AttributeError:
            print(f'using this for {style}')
            name, _ = utils.try_split(style, '@')
            style = Style(name)
            self.styles.setdefault(name, style)
        return style

    def remove(self, style):
        ''' used by styles editor '''
        try:
            del self.styles[style]
        except KeyError:
            self.styles = {n: s for n, s in self.styles.items() if s != style}

    def activate(self, style: str, menu_vars: list[tk.IntVar] = None):
        menu_vars = menu_vars or {}
        if style == 'sel':
            return
        name, code = utils.try_split(style, '@')
        if code:
            self.language_code = code
        menu_vars.setdefault(name, tk.IntVar()).set(1)
        self._current.add(style)

    def deactivate(self, style: str,  menu_vars: list[tk.IntVar] = None):
        menu_vars = menu_vars or {}
        name, _code = utils.try_split(style, '@')
        menu_vars.setdefault(name, tk.IntVar()).set(0)
        self._current.discard(style)

    def toggle(self, style: str):
        (self.deactivate if self.on(style) else self.activate)(style)

    def on(self, style):
        return style in self._current

    def clear(self, menu_vars: list[tk.IntVar] = None):
        menu_vars = menu_vars or {}
        self._current.clear()
        for var in menu_vars.values():
            var.set(0)

    def update(self, styles: list[str], menu_vars: list[tk.IntVar] = None):
        menu_vars = menu_vars or {}
        self.clear(menu_vars)
        for style in styles:
            self.activate(style, menu_vars)

    def modify_fontsize(self, amount):
        self.default.default_size += amount

    def reset_fontsize(self):
        self.default.reset_size()
