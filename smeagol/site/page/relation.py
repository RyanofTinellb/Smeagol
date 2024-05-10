from smeagol.site.page.node import Node
from smeagol.site import family


class Relation(Node):
    @property
    def _directory(self):
        return [self.directory.directory, self.names.copy()]

    def next_page(self):
        return self.new(family.next_entry(*self._directory))

    def previous_page(self):
        return self.new(family.previous_entry(*self._directory))
