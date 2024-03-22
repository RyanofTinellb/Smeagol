from typing import Self
from smeagol.utilities.utils import ignored


class Entries:
    def __init__(self, entries: dict[dict] | Self):
        self.entries = entries or {}
        with ignored(AttributeError):
            self.entries = self.entries.entries

    @property
    def root(self):
        return self.entries

    def __getitem__(self, name):
        return type(self)(self.entries['children'][name])

    def __setitem__(self, name, value):
        self.entries[name] = value

    def get(self, attr, default=None):
        return self.entries.get(attr, default)

    @property
    def name(self):
        for child in self.entries['children']:
            return child
        return ''
