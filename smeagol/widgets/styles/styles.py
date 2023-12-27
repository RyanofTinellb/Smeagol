from .style import Style


def get_name(style):
    return style.get('tags').get('name')


class Styles:
    def __init__(self, styles):
        self.default = None
        self.styles = {get_name(style): self.create_style(style)
                       for style in styles}
        self._current = set()

    @property
    def current(self):
        return list(self._current)

    def create_style(self, style=None):
        style = style or {}
        if self.default:
            return Style(**style, defaults=self.default)
        self.default = Style(**style)
        return self.default

    def __contains__(self, item):
        return item in self.styles

    def __iter__(self):
        return iter(self.styles.values())

    def __getitem__(self, name):
        if "-" in name:
            name, _language = name.split("-")
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

    def add(self, style):
        try:
            self.styles.setdefault(style.name, style)
        except AttributeError:
            style = style.split("-")
            name = style[0]
            language = len(style) > 1
            style = Style(
                [
                    {
                        "name": style[0],
                        "language": language,
                        "start": f"<{name}>",
                        "end": f"</{name}>",
                    }
                ]
            )
            self.styles.setdefault(name, style)
        return style

    def remove(self, style):
        try:
            del self.styles[style]
        except KeyError:
            self.styles = {n: s for n, s in self.styles.items() if s != style}

    def activate(self, style):
        self._current.add(style)

    def deactivate(self, style):
        self._current.discard(style)

    def clear(self):
        self._current.clear()

    def update(self, styles):
        self.clear()
        for style in styles:
            self.activate(style)
