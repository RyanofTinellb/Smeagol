from itertools import chain, zip_longest


class Node:
    def __init__(self, root=None, location=None):
        self.tree = root or {}
        self.location = location or []

    def __repr__(self):
        return f'Node: location = {self.location}'

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
            return type(self)(self.tree, location[:])
        except TypeError:
            return type(self)(self.tree, None)

    def find(self, node=None, location=None):
        node = node or self.tree
        location = location or self.location or []
        if len(location) == 1:
            return node['children'][location[0]]
        elif len(location) > 1:
            try:
                return self.find(node['children'][location[0]],
                                 location[1:])
            except TypeError:
                raise TypeError(type(node))
        else:
            return node

    def append(self, child):
        if self.num_children:
            self.children.append(child)
        else:
            self.children = [child]
        return self.youngest_granddaughter

    def delete(self):
        sisters = self.parent.children
        index = sisters.index(self.find())
        sisters.pop(index)

    def sister(self, index):
        if not len(self.location):
            raise IndexError('No such sister')
        location = self.location[:]
        children = self.new(location[:-1]).children
        if len(children) > location[-1] + index >= 0:
            location[-1] += index
            return self.new(location)
        else:
            raise IndexError('No such sister')

    @property
    def previous_sister(self):
        return self.sister(-1)

    @property
    def next_sister(self):
        return self.sister(1)

    def __getattr__(self, attr):
        if attr == 'children':
            return self.find().get('children', [])
        else:
            return getattr(super(Node, self), attr)

    def __setattr__(self, attr, value):
        if attr == 'children':
            self.find()['children'] = value
        else:
            super(Node, self).__setattr__(attr, value)

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
        elif _seen_children and self.is_root:
            raise IndexError('No more nodes!')
        else:
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
            return self.previous_sister._last_grandchild()
        except IndexError:
            location = self.location[:]
            if len(location):
                location.pop()
                return self.new(location)
            else:
                raise IndexError('No more nodes')

    def _last_grandchild(self, node=None):
        node = node or self.new()
        children = node.num_children
        if children:
            location = node.location[:] + [children - 1]
            return self._last_grandchild(self.new(location))
        else:
            return node

    @property
    def youngest_granddaughter(self):
        return self._last_grandchild()

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
        yield self.root
        for ancestor in self.ancestors:
            yield ancestor
        yield self.new()

    def unique_lineage(self, other):
        a, b = (self, other)
        superset, subset = [set(location.lineage)
                            for location in (self, other)]

        def level(node): return node.level
        for ancestor in sorted(superset - subset, key=level):
            yield ancestor
        if self.has_children:
            yield self.new(None)

    @property
    def matriarch(self):
        return self.ancestor(1)

    @property
    def matriarchs(self):
        for i, _ in enumerate(self.root.children):
            yield self.new([i])
        else:
            return

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
        else:
            try:
                return getattr(super(Node, self), 'eldest_daughter')
            except AttributeError:
                raise IndexError

    @property
    def youngest_daughter(self):
        if self.has_children:
            return self.new(self.location + [self.num_children - 1])
        else:
            return getattr(super(Node, self), 'youngest_daughter')

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

    def reunion(self, *groups):
        def location(node): return node.location
        relatives = sorted(set(chain(*groups)), key=location)
        for relative in relatives:
            yield relative

    @property
    def family(self):
        for relative in self.reunion(
                self.descendants, self.aunts, self.sisters):
            yield relative
