import random
import re

from .. import filesystem as fs


class English:
    def __init__(self, filenames):
        self.name = 'English'
        self.words = set()
        for filename in filenames:
            self.collate(fs.load_yaml(filename), self.words)
        self.words = list(self.words)

    def collate(self, page, words):
        words.update({word for line in page.get('text', []) for word in line.split()})
        for child in page.get('children', []):
            self.collate(child, self.words)

    @property
    def word(self):
        word = ''
        tries = 100
        while tries and not word:
            word = self._word
            tries -= 1
        return word
    
    @property
    def _word(self):
        return self._clean(random.choice(self.words)) if self.words else ''

    def _clean(self, word):
        for cleaner in self._cleaners:
            word = re.sub(cleaner, '', word)
        return word.lower()

    @property
    def _cleaners(self):
        return (
            r'\[.*?\]',
            r'<(ipa|high-lulani).*?/\1>',
            r'<.*?>',
            r'.*?>',
            r'<.*?',
            r'&.*?;',
            r'\W|\d',
        )
