from typing import Optional, Self

from smeagol.utilities.utils import ignored


def name(obj):
    return obj if isinstance(obj, str) else obj[0]

class Directory:
    def __init__(self, directory: Optional[list[list] | Self]):
        self.directory = directory or []
        with ignored(AttributeError):
            self.directory = self.directory.directory

    def __iter__(self):
        return iter(self.directory)

    def __getitem__(self, value: int | list[int]) -> Self:
        if isinstance(value, list):
            return self.new(self.find(value))
        return self.new(self.directory[value])

    def find(self, values: list[int]) -> list[list | str]:
        obj = self.directory
        for value in values:
            obj = obj[value]
        return obj

    def new(self, obj=None):
        obj = obj or self.directory
        return type(self)(obj)

    @property
    def children(self) -> list[str]:
        return [name(child) for child in self.directory[1:]]

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
        with ignored(IndexError):
            return self.directory[0]
