import os
import re

from smeagol.site.page.entry import Entry
from smeagol.utilities import utils


class Page(Entry):
    @property
    def lines(self):
        for line in self.fulltext.splitlines():
            yield line

    @property
    def fulltext(self):
        return ''.join(self._strings(self.text))

    def _strings(self, obj):
        if isinstance(obj, str):
            yield obj
        else:
            for elt in obj:
                yield from self._strings(elt)

    @property
    def link(self):
        names = [name.lower().replace(' ', '') for name in self.names[1:]]
        if not self.is_leaf:
            names += ['index']
        return names

    def link_to(self, other):
        with utils.ignored(AttributeError):
            other = other.link
        link = self.link
        if link == other:
            return ''
        utils.remove_common_prefix(link, other)
        other[-1], ext = utils.try_split(other[-1], '.', 'html')
        return (len(link)-1) * '../' + '/'.join(other) + '.' + ext

    @property
    def url(self):
        return os.path.join(*self.link) + '.html'

    @property
    def name(self):
        return self.names[-1]
