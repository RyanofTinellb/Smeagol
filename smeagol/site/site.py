from smeagol.site.page.page import Page
from smeagol.utilities import utils


class Site(Page):
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
