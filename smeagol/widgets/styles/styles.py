import json

from ... import utils
from . import Style
from ...conversion import Tagger


class Styles(Tagger):
    def __init__(self, styles=None):
        self.load(styles)

    def setup(self, styles=None):
        styles = styles or {}
        with utils.ignored(TypeError):
            styles = json.loads(styles)
        tagger = dict(default=Style(name='default'))
        if isinstance(styles, self.__class__):
            tagger.update({n: s.copy() for n, s in styles.styles.items()})
        else:
            tagger.update({n: Style(name=n, **s) for n, s in styles.items()})
        return tagger

    def load(self, styles=None):
        self.styles = self.setup(styles)

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
            style = Style(name=style[0], language=language)
            self.styles.setdefault(name, style)
        return style

    def remove(self, style):
        try:
            del self.styles[style]
        except KeyError:
            self.styles = {n: s for n, s in self.styles.items() if s != style}
