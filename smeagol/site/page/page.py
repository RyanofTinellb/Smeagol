import os
import re

from smeagol.site.page.entry import Entry
from smeagol.utilities import utils


class Page(Entry):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._analysis = {
            'terms': {},
            'lines': []
        }

    def __getattr__(self, attr):
        match attr:
            case 'terms' | 'lines':
                return self._analysis[attr]
        try:
            return super().__getattr__(attr)
        except AttributeError as e:
            name = type(self).__name__
            raise AttributeError(
                f"'{name}' object has no attribute '{attr}'") from e

    @property
    def sentences(self):
        yield from self.fulltext().splitlines()

    # @property
    def fulltext(self):
        return self.text.stringify()

    @property
    def link(self):
        names = [name.lower().replace(' ', '') for name in self.names[1:]]
        if not self.is_leaf:
            names += ['index']
        return names

    def link_to(self, other):
        fragment = ''
        with utils.ignored(AttributeError):
            other = other.link
        with utils.ignored(AttributeError):
            other, fragment = utils.try_split(other, '#')
            other = other.split('/')
        link = self.link
        if link == other:
            return ''
        utils.remove_common_prefix(link, other)
        hash_ = '#' if fragment else ''
        other[-1], ext = utils.try_split(other[-1], '.', 'html')
        return (len(link)-1) * '../' + '/'.join(other) + '.' + ext + hash_ + fragment

    @property
    def url(self):
        return os.path.join(*self.link) + '.html'

    @property
    def name(self):
        return self.names[-1]

    def analysis(self):
        punctuation = r'[#*‘“”_= ….,?!:;。$()/[\]\xa0\|]'
        self.terms.clear()
        for number, line in enumerate(self.sentences):
            self.lines.append(line)
            for term in re.split(punctuation, line.lower()):
                self._add_term(term, number)
        return self._analysis

    def _add_term(self, term, number):
        if not term:
            return
        self.terms.setdefault(term, set()).add(number)
