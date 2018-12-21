from collections import OrderedDict
from evolve import HighToColloquialLulani
import random
import json
import re

class RandomWords():
    def __init__(self, language=None):
        self.maximum = 20
        languages = OrderedDict()
        languages['en'] = English
        languages['hl'] = HighLulani
        languages['dl'] = DemoticLulani
        self.languages = languages
        self.select(language)

    def select(self, language):
        self.language = language
        try:
            language = language.lower()
            self.converter = self.languages[language]()
        except (IndexError, AttributeError, KeyError):
            self.converter = English()
        self.name = self.converter.name
        self.code = language
        self.number = len(self.languages)

    @property
    def words(self):
        return [self.converter.word for x in xrange(self.maximum)]

    def __iter__(self):
        return self


class English:
    def __init__(self):
        self.name = 'English'
        self.words = set()
        folder = ('c:/users/ryan/documents/tinellbianlanguages'
                  '/{0}/data.json')
        filenames = [
            'coelacanth',
            'writings',
        ]
        for filename in filenames:
            try:
                with open(folder.format(filename)) as page:
                    page = json.load(page)
                self.collate(page, self.words)
            except IOError:
                pass
        self.words = list(self.words)

    def collate(self, page, words):
        words.update({word for line in page.get('text', [])
                for word in line.split()})
        for child in page.get('children', []):
            self.collate(child, self.words)

    @property
    def word(self):
        choice = ''
        while not choice:
            choice = random.choice(self.words)
            for sub in (
                r'\[.*?\]',
                r'<(ipa|high-lulani).*?/\1>',
                r'<.*?>',
                r'.*?>',
                r'<.*?',
                r'&.*?;',
                r'\W|\d'
            ):
                choice = re.sub(sub, '', choice)
        return choice.lower()


class HighLulani:
    def __init__(self):
        self.name = 'High Lulani'
        self.geminate = 2

    @property
    def word(self):
        return u''.join(self.syllables)

    @property
    def consonant(self):
        lst = ['b', 'g', 'j', 'f', 'h', 'd', 'p', 'r', 't', 'm',
               'c', 'x', 'q', 'n', 'k', 'l', unichr(8217), 's']
        scale = [10, 10, 11, 12, 13, 14, 15, 16,
                 17, 19, 21, 24, 27, 32, 38, 47, 79, 82]
        return self.pick(lst, scale)

    @property
    def vowel(self):
        lst = ['a', 'i', 'u']
        scale = [4, 2, 1]
        return self.pick(lst, scale)

    @property
    def syllables(self):
        lst = [1, 2, 3, 4]
        scale = [7, 18, 15, 2]
        for i in xrange(self.pick(lst, scale)):
            yield self.double(self.syllable, i)

    @staticmethod
    def pick(lst, scale):
        rand = random.randint(1, sum(scale))
        try:
            sums = [sum(scale[:x]) for x in xrange(len(scale))]
            letter = [x <= rand for x in sums].index(False) - 1
            return lst[letter]
        except ValueError:
            return lst[-1]

    @property
    def syllable(self):
        return self.consonant + self.vowel

    def double(self, syllable, num):
        consonant, vowel = syllable
        if num and not random.randint(0, self.geminate):
            if consonant == unichr(8217):  # right single quote
                return unichr(660) + vowel # glottal stop
            return consonant + syllable
        return syllable

class DemoticLulani:
    def __init__(self):
        self.name = 'Demotic Lulani'
        self.lulani = HighLulani()
        self.vulgar = HighToColloquialLulani()
        self.rewrites = [
                ('&rsquo;', u"\u2019"),
                ('&middot;', u'\u00b7'),
                ('&#x294;', u'\u0294'),
                ('&eth;', u'\u00f0'),
                ('&thorn;', u'\u00fe'),
                ('&ouml;', u'\u00f6'),
                ('&uuml;', u'\u00fc'),
                ('&ntilde;', u'\u00f1'),
                ('&#x330;', u'\u0330'),
                ('h&#x330;', u'h\u0330'),
                ('&#x17e;', u'\u017e'),
                ('&#x1ee5;', u'\u1ee5'), # u with dot
                ('&#x1ecd;', u'\u1ecd'), # o with dot
                ('&#x1ecb;', u'\u1ecb'), # i with dot
                ('&#x323;', u'\u0323'), # lower dot
                ('&#x2c8;', u'\u02c8'),
                ('&#x2cc;', u'\u02cc')]

    @property
    def word(self):
        word = self.vulgar.evolve(self._word)[-1]
        for rewrite in self.rewrites:
            word = word.replace(*rewrite)
        return word

    @property
    def _word(self):
        num = random.randint(0, 6)
        if num < 2:
            return '{0}{1}'.format(self.lulani_word, self.lulani_word)
        else:
            return self.lulani_word

    @property
    def lulani_word(self):
        word = self.lulani.word
        return word.replace(
            unichr(8217), "&rsquo;").replace(
            unichr(660), "&#x294;")
