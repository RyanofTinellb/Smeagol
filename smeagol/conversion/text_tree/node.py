from typing import Self


class Node:
    def __init__(self, parent: Self = None, name: str = '') -> None:
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

    def nodes(self):
        for child in self.children:
            if not isinstance(child, str):
                yield child
                yield from child.nodes()

    def stringify(self, skip=None):
        return ''.join([self._strings(child, skip) for child in self.children])

    def _strings(self, child, skip=None):
        if isinstance(child, str):
            return child
        if child.name and child.name == skip:
            return ''
        return child.stringify(skip)

    def __iter__(self):
        return iter(self.children)

    def __getitem__(self, key):
        return self.children[key]

    @property
    def first_child(self):
        return self.children[0]

    @property
    def other_child(self):
        return self.children[-1]

    def __str__(self):
        return f'{self.open_tag}{self.middle_text}{self.close_tag}'

    def pprint(self, lvl=0):
        print(' ' * lvl + self.name.replace('\n', '\\n'))
        for child in self.children:
            self._pprint(child, lvl+2)

    @staticmethod
    def _pprint(child, lvl):
        try:
            child.pprint(lvl)
        except AttributeError:
            text = child.replace('\n', '\\n')
            print(' ' * lvl + f'"{text}"')
