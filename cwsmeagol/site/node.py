from itertools import chain
from cwsmeagol.utils import urlform

def unique(iter):
    old = Node(None, None)
    for k in iter:
        if old <> k:
            yield k
        old = k

class Node(object):
    def __init__(self, root, location):
        self.root = root
        self.location = location

    def __getattr__(self, attr):
        if attr in ('name', 'date', 'text', 'children', 'hyperlink', 'flatname'):
            return self.find()[attr]
        else:
            raise AttributeError("{0} instance has no attribute '{1}'".format(
                    self.__class__.__name__, attr))

    def __repr__(self):
        return 'Node: location = {0}'.format(self.location)

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

    def new(self, location):
        return type(self)(self.root, location[:])

    def find(self, node=None, location=None):
        node = node or self.root
        location = location or self.location
        if len(location) == 1:
            return node['children'][location[0]]
        elif len(location) > 1:
            try:
                return self.find(node['children'][location[0]], location[1:])
            except TypeError:
                raise TypeError(type(node))
        else:
            return node

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

    @property
    def num_children(self):
        return len(self.children)

    @property
    def has_children(self):
        return self.num_children > 0

    @property
    def is_leaf(self):
        return not self.has_children

    def next(self, _seen_children=False):
        if not _seen_children and self.has_children:
            self.location += [0]
            return self
        else:
            try:
                return self.next_sister()
            except IndexError:
                self.location.pop()
                return self.next(_seen_children=True)

    def previous(self):
        try:
            self._last_grandchild()
            return self
        except IndexError:
            if len(self.location):
                self.location.pop()
                return self
            else:
                raise IndexError('No more nodes')

    def _last_grandchild(self):
        children = num_children()
        if children:
            self.location += [children - 1]
            self._last_grandchild()

    def cousin_degree(self, destination):
        try:
            return [i != j for i, j in
                    zip(self.location, destination.location)].index(True) + 1
        except ValueError:
            return min(map(len, [self.location, destination.location]))

    def startswith(self, destination):
        return list(self.location[:len(destination.location)]
                                            ) == list(destination.location)

    @property
    def ancestors(self):
        for i in xrange(len(self.location) - 1):
            yield self.new(self.location[:i + 1])

    def __sub__(self, other):
        return self.unshared_ancestors(other)

    def unshared_ancestors(self, other):
        source, destination = [set(location.ancestors())
                    for location in (self, other)]
        for ancestor in sorted(source - destination):
            yield ancestor
        yield self

    @property
    def matriarchs(self):
        for i, _ in enumerate(self.root['children']):
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
        relatives = unique(sorted(chain(*groups)))
        for relative in relatives:
            yield relative

    @property
    def family(self):
        for relative in self.reunion(
                    self.descendants, self.aunts, self.sisters):
            yield relative

    @property
    def url(self):
        return urlform(self.name)
