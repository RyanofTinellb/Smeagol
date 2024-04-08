from typing import Self
from smeagol.utilities import utils


class Entries:
    def __init__(self, entries: dict[dict] | Self):
        self.entries = entries or {}
        with utils.ignored(AttributeError):
            self.entries = self.entries.entries

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
        return self.entries.get(attr, default)

    @property
    def children(self):
        return self.entries.get('children', {})

    @property
    def name(self):
        for child in self.children:
            return child
        return ''
