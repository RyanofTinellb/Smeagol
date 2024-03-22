from itertools import chain
from smeagol.site.directory import Directory
from smeagol.site.entries import Entries


class Node:
    def __init__(self, directory=None, entries=None, names=None):
        self.directory = Directory(directory)
        self.entries = Entries(entries)
        self.names = names or [self.directory.name or self.entries.name]

    @property
    def name(self):
        return self.names[-1]
    
    @property
    def location(self):
        location = []
        obj = self.directory
        for name in self.names[1:]:
            index = self._index(obj, name)
            location.append(index)
            obj = obj[index]
        return location

    @staticmethod
    def _index(obj, name):
        for i, elt in enumerate(obj):
            if elt[0] == name:
                return i
        raise IndexError

    @property
    def data(self):
        obj = self.entries
        for name in self.names:
            obj = obj[name]
        return obj

    def __repr__(self):
        return f'Node: names = {self.names}'

    def __hash__(self):
        return hash(tuple(self.location))

    def __eq__(self, other):
        return self.location == other.location

    def __lt__(self, other):
        return self.location < other.location

    def __gt__(self, other):
        return self.location > other.location

    def __ge__(self, other):
        return self.location >= other.location

    def __le__(self, other):
        return self.location <= other.location

    def __ne__(self, other):
        return self.location != other.location

    def __len__(self):
        return len(self.location)

    @property
    def level(self):
        return len(self)

    def new(self, location=None):
        if location is None:
            location = self.location
        try:
            return type(self)(self.directory, self.entries, self.names[:])
        except TypeError:
            return type(self)(self.directory, self.entries, None)

    def append(self, child):
        # pylint: disable=E0203, W0201
        if self.num_children:
            self.children.append(child)
        else:
            self.children = [child]
        return self.youngest_granddaughter

    def delete(self):
        sisters = self.parent.children
        index = sisters.index(self.find)
        sisters.pop(index)

    def sister(self, index):
        if not self.location:  # at the root node
            raise IndexError('No such sister')
        location = self.location[:]
        children = self.new(location[:-1]).children
        if len(children) > location[-1] + index >= 0:
            location[-1] += index
            return self.new(location)
        raise IndexError('No such sister')

    @property
    def previous_sister(self):
        return self.sister(-1)

    @property
    def next_sister(self):
        return self.sister(1)

    def __getattr__(self, attr):
        match attr:
            case 'children':
                return self.data.get('children', [])
            case _default:
                try:
                    return super().__getattr__(attr)
                except AttributeError as e:
                    name = self.__class__.__name__
                    raise AttributeError(
                        f"'{name}' object has no attribute '{attr}'") from e

    def __setattr__(self, attr, value):
        match attr:
            case 'children':
                self.data['children'] = value
            case _default:
                super().__setattr__(attr, value)

    @property
    def num_children(self):
        return len(self.children)

    @property
    def has_children(self):
        return self.num_children > 0

    @property
    def is_leaf(self):
        return not self.has_children

    @property
    def is_root(self):
        return len(self.location) == 0

    def next(self, _seen_children=False):
        if not _seen_children and self.has_children:
            return self.new(self.location + [0])
        if _seen_children and self.is_root:
            raise IndexError('No more nodes!')
        try:
            return self.next_sister
        except IndexError:
            return self.new(self.location[:-1]).next(_seen_children=True)

    @property
    def successor(self):
        return self.next()

    @property
    def predecessor(self):
        return self.previous()

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

    def distance(self, destination):
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
    def root(self):
        return self.new([])

    @property
    def parent(self):
        return self.new(self.location[:-1])

    def ancestor(self, level):
        return self.new(self.location[:level])

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
    def matriarch(self):
        return self.ancestor(1)

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
