from typing import Optional, Self

from smeagol.utilities import utils


def name(obj):
    return obj if isinstance(obj, str) else obj[0]


class Directory:
    def __init__(self, directory: Optional[list[list] | Self],
                        names: list[str] = None,
                        subdirectory: bool = False):
        self.directory = directory or []
        with utils.ignored(AttributeError):
            self.directory = self.directory.directory
        self.names = names or []
        if subdirectory:
            self.names.append(self.name)

    def __iter__(self):
        return iter(self.directory)

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
        with utils.ignored(IndexError):
            return self.directory[0]
