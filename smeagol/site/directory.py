from typing import Optional, Self

from smeagol.utilities import utils


def get_name(obj):
    return obj if isinstance(obj, str) else obj[0]


def get_index(obj, name):
    for i, elt in enumerate(obj):
        if elt[0] == name:
            return i
    raise ValueError(f'{get_name(obj)} has no item {name}')


class Directory:
    def __init__(self, directory: Optional[list[list] | Self] = None,
                 names: list[str] = None,
                 subdirectory: bool = False):
        self.names = names or ['']
        self.directory = directory or [self.names[0]]
        with utils.ignored(AttributeError):
            self.directory = self.directory.directory
        if subdirectory:
            self.names.append(self.name)

    def __iter__(self):
        return self._rec(self.directory)

    def _rec(self, obj, names=None):
        names = [*(names or []), obj[0]]
        yield names
        for elt in obj[1:]:
            yield from self._rec(elt, names)

    def __getitem__(self, value: int | list[int]) -> Self:
        if isinstance(value, list):
            return self.subdirectory(self.find(value))
        return self.subdirectory(self.directory[value])

    def find(self, values: list[int]) -> list[str]:
        return utils.recurse(self, values).names

    def new(self, names=None):
        names = names or self.names
        return type(self)(self.directory, names)

    def subdirectory(self, obj=None, names=None):
        return type(self)(directory=obj, names=names, subdirectory=True)

    def location(self, names) -> list[int]:
        location = []
        obj = self.directory
        for name in names[1:]:
            index = get_index(obj, name)
            location.append(index)
            obj = obj[index]
        return location

    def add(self, names):
        obj = self.directory
        for name in names[1:]:
            try:
                index = get_index(obj, name)
            except ValueError:
                obj.append([name])
                index = len(obj) - 1
            obj = obj[index]

    def remove(self, names):
        obj = self.directory
        name = names.pop()
        for entry in names[1:]:
            index = get_index(obj, entry)
            obj = obj[index]
        index = get_index(obj, name)
        if len(obj[index]) != 1:
            raise IndexError(f'Unable to remove non-empty subdirectory {name}')
        obj.pop(get_index(obj, name))

    def pprint(self) -> None:
        self._pprint(self.directory)

    def _pprint(self, obj, indices: str = '') -> None:
        if isinstance(obj, str):
            print(indices[:-1], obj)
            return
        for i, elt in enumerate(obj):
            self._pprint(elt, indices + str(i))

    @property
    def name(self) -> str:
        with utils.ignored(IndexError):
            return self.directory[0]
