from itertools import chain, izip_longest


class Node(object):
    def __init__(self, root, location):
        self.tree = root
        self.location = location

    def __repr__(self):
        return 'Node: location = {0}'.format(self.location)

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
        return self.location <> other.location

    def __len__(self):
        return len(self.location)

    def new(self, location):
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

    def delete(self):
        sisters = self.parent.children
        index = sisters.index(self.find())
        sisters.pop(index)

    def sister(self, index):
        if not len(self.location):
            raise IndexError('No such sister')
        children = self.new(self.location[:-1]).children
        if len(children) > self.location[-1] + index >= 0:
            self.location[-1] += index
            return self
        else:
            raise IndexError('No such sister')

    def previous_sister(self):
        return self.sister(-1)

    def next_sister(self):
        return self.sister(1)

    def __getattr__(self, attr):
        if attr is 'children':
            return self.find().get('children', [])
        else:
            return getattr(super(Node, self), attr)

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
            self.location += [0]
            return self
        else:
            try:
                return self.next_sister()
            except IndexError:
                try:
                    self.location.pop()
                    return self.next(_seen_children=True)
                except IndexError:
                    raise StopIteration

    @property
    def successor(self):
        try:
            return self.new(self.location).next()
        except StopIteration:
            raise IndexError('No more nodes!')

    @property
    def predecessor(self):
        return self.new(self.location).previous()

    def previous(self):
        try:
            self.previous_sister()
            self._last_grandchild()
            return self
        except IndexError:
            if len(self.location):
                self.location.pop()
                return self
            else:
                raise IndexError('No more nodes')

    def _last_grandchild(self):
        children = self.num_children
        if children:
            self.location += [children - 1]
            self._last_grandchild()

    def distance(self, destination):
        self, destination = [x.location for x in (self, destination)]
        try:
            dist = [i != j for i, j in
                    zip(self, destination)].index(True)
            return len(self) - dist
        except ValueError:
            return min(map(len, [self, destination]))

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

    @property
    def ancestors(self):
        for i in xrange(len(self.location) - 1):
            yield self.new(self.location[:i + 1])

    @property
    def lineage(self):
        yield self.root
        for ancestor in self.ancestors:
            yield ancestor
        yield self

    def unique_lineage(self, other):
        superset, subset = [set(location.lineage)
                                for location in (self, other)]
        level = lambda node: node.level
        for ancestor in sorted(superset - subset, key=level):
            yield ancestor
        if self.has_children:
            yield self.new(None)

    @property
    def matriarch(self):
        return self.new([self.location[0]])

    @property
    def matriarchs(self):
        for i, _ in enumerate(self.root.children):
            yield self.new([i])
        else:
            raise StopIteration

    @property
    def sisters(self):
        if len(self.location) == 0:
            raise StopIteration
        location = self.location[:-1]
        for child in xrange(self.new(location).num_children):
            yield self.new(location + [child])

    @property
    def aunts(self):
        for ancestor in self.ancestors:
            for sister in ancestor.sisters:
                yield self.new(sister.location)

    @property
    def daughters(self):
        for child in xrange(self.num_children):
            yield self.new(self.location + [child])

    @property
    def eldest_daughter(self):
        if self.has_children:
            return self.new(self.location + [0])
        else:
            return getattr(super(Node, self), 'eldest_daughter')

    @property
    def descendants(self):
        generation = len(self.location)
        location = self.location[:]
        next = self.new(location).next()
        while len(next.location) <> generation:
            yield next
            try:
                next = self.new(next.location).next()
            except IndexError:
                raise StopIteration

    def reunion(self, *groups):
        location = lambda node: node.location
        relatives = sorted(set(chain(*groups)), key=location)
        for relative in relatives:
            yield relative

    @property
    def family(self):
        for relative in self.reunion(
                self.descendants, self.aunts, self.sisters):
            yield relative
