from smeagol.site.page.page import Page
from smeagol.utilities import utils


class Site(Page):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current = self.root

    def __iter__(self):
        for names in self.entries:
            yield self.new(names)

    def __len__(self):
        return sum(1 for page in self)

    @property
    def hierarchy(self):
        for names in self.directory:
            yield self.new(names)

    @property
    def root(self):
        return self

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
            names.append(entry.name)
            for word, line_numbers in new_words.items():
                line_numbers = utils.increment(line_numbers, by=base)
                locations = {str(entry_number): line_numbers}
                try:
                    words[word].update(locations)
                except KeyError:
                    words[word] = locations
        return {'terms': words,
                'sentences': sentences,
                'urls': urls,
                'names': names}
