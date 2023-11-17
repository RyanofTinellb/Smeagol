import json

from ...conversion import api as conversion
from ...utilities import utils
from .style import Style


class Styles(conversion.Tagger):
    def __init__(self, styles):
        self.default = None
        super().__init__(styles)

    
    def create_tag(self, rank=0, tag=None):
        tag = tag or {}
        if self.default:
            return Style(rank, **tag, defaults=self.default)
        self.default = Style(rank, **tag)
        return self.default
    
    @property
    def styles(self):
        return self.tags

    def __contains__(self, item):
        return item in self.styles

    def __iter__(self):
        return iter(self.styles.values())

    def __getitem__(self, name):
        if '-' in name:
            name, language = name.split('-')
        return self.styles[name]

    def __setitem__(self, name, value):
        self.styles[name] = value

    def copy(self):
        return Styles(self)

    @property
    def names(self):
        return list(self.keys())

    @property
    def keys(self):
        return self.styles.keys

    @property
    def values(self):
        return self._items.values

    @property
    def items(self):
        return self._items.items

    @property
    def _items(self):
        return {n: s.style for n, s in self.styles.items()}

    def update(self, styles):
        self.styles = styles.styles

    def add(self, style):
        try:
            self.styles.setdefault(style.name, style)
        except AttributeError:
            style = style.split('-')
            name = style[0]
            language = len(style) > 1
            style = Style(name=style[0], language=language, start=f'<{name}>', end=f'</{name}>')
            self.styles.setdefault(name, style)
        return style

    def remove(self, style):
        try:
            del self.styles[style]
        except KeyError:
            self.styles = {n: s for n, s in self.styles.items() if s != style}
