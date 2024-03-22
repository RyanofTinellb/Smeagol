from typing import Self, Optional
from smeagol.utilities.utils import ignored

class Directory:
    def __init__(self, directory: Optional[list[list] | Self]):
        self.directory = directory or []
        with ignored(AttributeError):
            self.directory = self.directory.directory

    def __iter__(self):
        return iter(self.directory)

    def __getitem__(self, value):
        return type(self)(self.directory[value])

    def pprint(self):
        self._pprint(self.directory)

    def _pprint(self, obj, indices: str = ''):
        if isinstance(obj, str):
            print(indices[:-1], obj)
            return
        for i, elt in enumerate(obj):
            self._pprint(elt, indices + str(i))

    @property
    def name(self):
        with ignored(IndexError):
            return self.directory[0]
