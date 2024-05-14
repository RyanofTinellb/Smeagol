from typing import Self, Optional
from smeagol.utilities import utils


class Entries:
    def __init__(self, entries: Optional[dict[dict]] | Self = None):
        self.entries = entries
        with utils.ignored(AttributeError):
            self.entries = self.entries.entries

    def __iter__(self):
        return self._rec(self.entries)

    def _rec(self, item, names=None):
        names = names or ()
        with utils.ignored(AttributeError):
            for name, elt in item.get('children', {}).items():
                yield ([*names, name])
                yield from self._rec(elt, (*names, name))

    def add(self, names: list[str]):
        obj: dict = self.entries
        for name in names:
            obj = obj.setdefault('children', {}).setdefault(name, {})

    def remove(self, names: list[str]):
        name = names.pop()
        parent = self[names].entries['children']
        if parent[name].get('children') or parent[name].get('text'):
            raise IndexError(f'Unable to remove non-empty entry {name}')
        parent.pop(name, None)

    @property
    def root(self):
        return self.entries

    def __getitem__(self, value: str | list[str]):
        if isinstance(value, str):
            return type(self)(self.children[value])
        return utils.recurse(self, value)

    def __setitem__(self, name, value):
        self.entries[name] = value

    def get(self, attr, default=None):
        return self.entries.setdefault(attr, default)

    @property
    def children(self):
        return self.entries.get('children', {})

    @property
    def name(self):
        for child in self.children:
            return child
        return ''
