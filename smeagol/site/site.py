from ..utilities import utils
from .page import Page


class Site:
    def __init__(self, tree=None):
        self.tree = tree or {}

    def __iter__(self):
        return self.iterator

    @property
    def iterator(self):
        node = self.root
        while True:
            yield node
            try:
                node = node.next()
            except IndexError:
                return

    def __getitem__(self, name):
        entry = Page(self.tree, [])
        count = 0
        try:
            while entry.name != name != count:
                entry = entry.successor
                count += 1
        except IndexError as e:
            raise (KeyError if type(name) in (list, str) else IndexError)(name) from e
        return entry

    @property
    def root(self):
        return self[0]

    def replace_all(self, old, new):
        for entry in self:
            entry.replace(old, new)

    def regex_replace_all(self, pattern, repl):
        for entry in self:
            entry.regex_replace(pattern, repl)

    @property
    def analysis(self):
        words = {}
        sentences = []
        urls = []
        names = []
        for entry_number, entry in enumerate(self):
            base = len(sentences)
            analysis = entry.analysis
            new_words = analysis['words']
            sentences += analysis['sentences']
            urls.append(entry.link)
            names.append(utils.buyCaps(entry.name))
            for word, line_numbers in new_words.items():
                line_numbers = utils.increment(line_numbers, by=base)
                locations = {str(entry_number): line_numbers}
                try:
                    words[word].update(locations)
                except KeyError:
                    words[word] = locations
        return dict(terms=words,
                    sentences=sentences,
                    urls=urls,
                    names=names)