from smeagol.site.page.node import Node
from smeagol.site import family
from smeagol.utilities import utils


def skip(names):
    return len(names) == 2


class Relation(Node):
    # @property
    def _directory(self, names=None):
        names = names or self.names
        return [self.directory.directory, names.copy()]

    def next_page(self):
        node = family.next_entry(*self._directory())
        while skip(node):
            node = family.next_entry(*self._directory(node))
        return self.new(node)

    def previous_page(self):
        node = family.previous_entry(*self._directory())
        while skip(node):
            node = family.previous_entry(*self._directory(node))
        return self.new(node)

    def reunion(self, groups):
        k = set()
        for group in groups:
            k.update(set(self.groups[group]()))
        return k

    def matriarchs(self):
        with utils.ignored(IndexError):
            for matriarch in family.generation(*self._directory(), 2):
                yield self.new(matriarch)

    def siblings(self):
        for sibling in family.siblings(*self._directory()):
            if not skip(sibling):
                yield self.new(sibling)

    def descendants(self):
        for descendant in family.descendants(*self._directory()):
            if not skip(descendant):
                yield self.new(descendant)

    def children(self):
        for child in family.children(*self._directory()):
            if skip(child):
                yield from self._skipchildren(child)
                return
            yield self.new(child)

    def _skipchildren(self, relative):
        for child in family.children(*self._directory(relative)):
            yield self.new(child)

    def lineage(self):
        for ancestor in family.lineage(self.names):
            if not skip(ancestor):
                yield self.new(ancestor)

    def aunts(self):
        for aunt in family.aunts(*self._directory()):
            if not skip(aunt):
                yield self.new(aunt)

    def heirs(self):
        for heir in family.descendants(*self._directory()):
            if len(heir) <= 4 and not skip(heir):
                yield self.new(heir)

    @property
    def groups(self):
        return {
            'matriarchs': self.matriarchs,
            'siblings': self.siblings,
            'descendants': self.descendants,
            'children': self.children,
            'lineage': self.lineage,
            'heirs': self.heirs,
            'aunts': self.aunts
        }
