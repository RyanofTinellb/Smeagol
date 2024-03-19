from typing import Self

# -------------------------------------- ↑ refactored ↑ ---------------------------------------------------- #
class Node:
    def __init__(self, parent: Self=None, name: str='') -> None:
        self.parent = parent
        self.name = name
        self.children = []

    @property
    def open_tag(self):
        return f'<{self.name}>' if self.name else ''

    @property
    def close_tag(self):
        return f'</{self.name}>' if self.name else ''

    @property
    def middle_text(self):
        return ''.join((str(child) for child in self.children))

    def __repr__(self):
        return f'Node object, name: {self.name}'

    def add(self, child):
        self.children.append(child)

    def __iter__(self):
        return iter(self.children)

    def __str__(self):
        return f'{self.open_tag}{self.middle_text}{self.close_tag}'

    def pprint(self, lvl=0):
        print(' ' * lvl + self.name)
        for child in self.children:
            self._pprint(child, lvl+2)

    @staticmethod
    def _pprint(child, lvl):
        try:
            child.pprint(lvl)
        except AttributeError:
            if child == '\n':
                return
            print(' ' * lvl + '"' + child + '"')
