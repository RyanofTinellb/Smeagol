from typing import Self

from smeagol.site.directory import Directory
from smeagol.site.entries import Entries
from smeagol.utilities.utils import ignored


class Node:
    def __init__(self, directory=None, entries=None, names=None):
        self.directory = Directory(directory, names)
        self.entries = Entries(entries)
        self.names = names or [self.directory.name or self.entries.name]
        self._data = None

    @property
    def location(self) -> list[int]:
        return self.directory.location(self.names)

    def _find(self, location: list[int]) -> Self:
        obj = self.directory
        names = [obj.name]
        for place in location:
            names.append(self._locate(obj, place))
        return type(self)(self.directory, self.entries, names)

    def _locate(self, obj: Directory, place: int):
        try:
            return obj[place]
        except TypeError as e:
            raise KeyError(f'{obj.name} has no child {place}') from e

    @property
    def data(self) -> dict:
        if not self._data:
            self._data = self.entries[self.names]
        return self._data

    def __hash__(self):
        return hash('/'.join(self.names))

    def __eq__(self, other):
        return self.names == other.names

    def __repr__(self):
        return f'Node: names = {self.names}'

    @property
    def hierarchy(self):
        for names in self.directory:
            yield self.new(names)

    def new(self, values: list[str] | list[int] = None) -> Self:
        values = values or [self.entries.name]
        with ignored(TypeError):
            values = self.directory[values].names  # values are integers
        return type(self)(self.directory, self.entries, values[:])

    def __getitem__(self, values: list[str] | list[int]):
        return self.new(values)

    def __getattr__(self, attr):
        match attr:
            case 'name':
                value = self.names[-1]
            case 'level':
                value = max(0, len(self.names)-1)
            case 'kids':
                value = self.data.children
            case 'num_children':
                value = len(self.kids)
            case 'has_children':
                value = self.num_children > 0
            case 'is_leaf':
                value = not self.has_children
            case 'is_root':
                value = self.level == 0
            case 'root':
                value = self.new([])
            case _default:
                try:
                    value = super().__getattr__(attr)
                except AttributeError as e:
                    name = self.__class__.__name__
                    raise AttributeError(
                        f"'{name}' object has no attribute '{attr}'") from e
        return value
