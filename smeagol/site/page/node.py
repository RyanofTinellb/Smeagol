from itertools import chain
from typing import Self

from smeagol.site.directory import Directory
from smeagol.site.entries import Entries
from smeagol.utilities.utils import ignored


class Node:
    def __init__(self, directory=None, entries=None, names=None):
        self.directory = Directory(directory, names)
        self.entries = Entries(entries)
        self.names = names or [self.directory.name or self.entries.name]

    @property
    def location(self):
        location = []
        obj = self.directory
        for name in self.names[1:]:
            index = self._index(obj, name)
            location.append(index)
            obj = obj[index]
        return location

    def _index(self, obj, name):
        for i, elt in enumerate(obj):
            if elt[0] == name:
                return i
        raise IndexError(f'{obj.name} has no item {name}')

    def _find(self, location: list[int]) -> Self:
        obj = self.directory
        names = [obj.name]
        for place in location:
            names.append(self._locate(obj, place))
        return type(self)(self.directory, self.entries, names)

    def _locate(self, obj, place):
        try:
            return obj[place]
        except TypeError as e:
            raise KeyError(f'{obj.name} has no child {place}') from e

    @property
    def data(self):
        obj = self.entries
        for name in self.names:
            obj = obj[name]
        return obj

    def __repr__(self):
        return f'Node: names = {self.names}'

    def new(self, values: list[str] | list[int] = None) -> Self:
        values = values or self.names
        with ignored(TypeError):
            values = self.directory[values].names[:-1]
        return type(self)(self.directory, self.entries, values[:])

    def append(self, child):
        # pylint: disable=E0203, W0201
        if self.num_children:
            self.children.append(child)
        else:
            self.children = [child]
        return self.youngest_granddaughter

    def delete(self):
        sisters = self.parent.children
        index = sisters.index(self._find)
        sisters.pop(index)

    def sister(self, index):
        if not self.location:  # at the root node
            raise IndexError('No such sister')
        location = self.location[:-1]
        children = self.new(location[:-1]).children
        if len(children) > location[-1] + index >= 0:
            location[-1] += index
            return self.new(location)
        raise IndexError('No such sister')

    def next(self, _seen_children=False):
        if not _seen_children and self.has_children:
            return self.new(self.location + [0])
        if _seen_children and self.is_root:
            raise IndexError('No more nodes!')
        try:
            return self.next_sister
        except IndexError:
            return self.new(self.location[:-1]).next(_seen_children=True)

    def __getitem__(self, values: list[str] | list[int]):
        return self.new(values)

    def __getattr__(self, attr):
        match attr:
            case 'name':
                value = self.names[-1]
            case 'level':
                value = len(self.location)
            case 'previous_sister':
                value = self.sister(-1)
            case 'next_sister':
                value = self.sister(1)
            case 'children':
                value = [self.new(self.names + [child])
                         for child in self.directory[self.location].children]
            case 'num_children':
                value = len(self.children)
            case 'has_children':
                value = self.num_children > 0
            case 'is_leaf':
                value = not self.has_children
            case 'is_root':
                value = self.level == 1
            case 'successor':
                value = self.next()
            case 'predecessor':
                value = self.previous()
            case 'root':
                value = self.new([])
            case 'parent':
                value = self.new(self.location[:-1])
            case 'matriarch':
                value = self.ancestor(1)
            case _default:
                try:
                    value = super().__getattr__(attr)
                except AttributeError as e:
                    name = self.__class__.__name__
                    raise AttributeError(
                        f"'{name}' object has no attribute '{attr}'") from e
        return value

    def ancestor(self, level):
        return self.new(self.location[:level])

    def previous(self):
        try:
            return self.previous_sister.youngest_descendant
        except IndexError as e:
            location = self.location[:]
            if location:
                location.pop()
                return self.new(location)
            raise IndexError('No more nodes') from e

    def _youngest_descendant(self, node=None):
        node = node or self.new()
        children = node.num_children
        if children:
            location = node.location[:] + [children - 1]
            return self._youngest_descendant(self.new(location))
        return node

    @property
    def youngest_descendant(self):
        return self._youngest_descendant()

    def _distance(self, destination):
        source, destination = [x.location for x in (self, destination)]
        try:
            dist = [i != j for i, j in
                    zip(source, destination)].index(True)
            return len(source) - dist
        except ValueError:
            return min(list(map(len, [source, destination])))

    def descendant_of(self, other):
        tail = self.location[:other.level]
        return other == self.new(tail)

    def ancestor_of(self, other):
        return other.descendant_of(self)

    def related_to(self, other):
        return self.descendant_of(other) or self.ancestor_of(other)

    @property
    def ancestors(self):
        for i in range(self.level - 1):
            yield self.new(self.location[:i + 1])

    @property
    def lineage(self):
        if not self.is_root:
            yield self.root
        for ancestor in self.ancestors:
            yield ancestor
        yield self.new()

    def unique_lineage(self, other):
        superset, subset = [set(location.lineage)
                            for location in (self, other)]

        for ancestor in sorted(superset - subset, key=lambda node: node.level):
            yield ancestor
        if self.has_children:
            yield self.new(None)

    @property
    def matriarchs(self):
        for i, _child in enumerate(self.root.children):
            yield self.new([i])

    @property
    def sisters(self):
        if len(self.location) == 0:
            return
        location = self.location[:-1]
        for child in range(self.new(location).num_children):
            yield self.new(location + [child])

    @property
    def aunts(self):
        for ancestor in self.ancestors:
            for sister in ancestor.sisters:
                yield self.new(sister.location)

    @property
    def daughters(self):
        for child in range(self.num_children):
            yield self.new(self.location + [child])

    @property
    def eldest_daughter(self):
        if self.has_children:
            return self.new(self.location + [0])
        try:
            return getattr(super(), 'eldest_daughter')
        except AttributeError as e:
            raise IndexError from e

    @property
    def youngest_daughter(self):
        if self.has_children:
            return self.new(self.location + [self.num_children - 1])
        return getattr(super(), 'youngest_daughter')

    @property
    def descendants(self):
        if not self.has_children:
            return
        node = self.eldest_daughter
        while node.level > self.level:
            yield node
            try:
                node = node.next()
            except IndexError:
                return

    @staticmethod
    def reunion(*groups):
        relatives = sorted(set(chain(*groups)), key=lambda n: n.location)
        for relative in relatives:
            yield relative

    @property
    def family(self):
        for relative in self.reunion(
                self.descendants, self.aunts, self.sisters):
            yield relative
