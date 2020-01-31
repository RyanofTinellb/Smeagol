from collections import OrderedDict
from .evolve import HighToDemoticLulani
import random
import json
import re


class RandomWords:
    def __init__(self, language=None, sample_texts=''):
        self.maximum = 15
        self.sample_texts = sample_texts
        languages = OrderedDict()
        languages['en'] = English
        languages['hl'] = HighLulani
        languages['dl'] = DemoticLulani
        self.languages = languages
        self.select(language)

    def select(self, language=None):
        self.language = language
        try:
            language = language.lower()
            self.converter = self.languages[language]()
        except:
            self.converter = English(self.sample_texts)
        self.name = self.converter.name
        self.code = language
        self.number = len(self.languages)

    @property
    def words(self):
        return [self.converter.word for x in range(self.maximum)]

    def __iter__(self):
        return self


class English:
    def __init__(self, sample_texts):
        self.name = 'English'
        self.words = set()
        filenames = sample_texts.split(';')
        for filename in filenames:
            try:
                with open(filename, encoding='utf-8') as page:
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
        if self.words:
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
        return ''.join(self.syllables)

    @property
    def consonant(self):
        lst = ['b', 'g', 'j', 'f', 'h', 'd', 'p', 'r', 't', 'm',
               'c', 'x', 'q', 'n', 'k', 'l', chr(8217), 's']
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
        for i in range(self.pick(lst, scale)):
            yield self.double(self.syllable, i)

    @staticmethod
    def pick(lst, scale):
        rand = random.randint(1, sum(scale))
        try:
            sums = [sum(scale[:x]) for x in range(len(scale))]
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
            if consonant == chr(8217):  # right single quote
                return chr(660) + vowel  # glottal stop
            return consonant + syllable
        return syllable


class DemoticLulani:
    def __init__(self):
        self.name = 'Demotic Lulani'
        self.lulani = HighLulani()
        self.vulgar = HighToDemoticLulani()
        self.rewrites = [
            ('&rsquo;', "\u2019"),
            ('&middot;', '\u00b7'),
            ('&#x294;', '\u0294'),
            ('&eth;', '\u00f0'),
            ('&thorn;', '\u00fe'),
            ('&ouml;', '\u00f6'),
            ('&uuml;', '\u00fc'),
            ('&ntilde;', '\u00f1'),
            ('&#x330;', '\u0330'),
            ('h&#x330;', 'h\u0330'),
            ('&#x17e;', '\u017e'),
            ('&#x1ee5;', '\u1ee5'),  # u with dot
            ('&#x1ecd;', '\u1ecd'),  # o with dot
            ('&#x1ecb;', '\u1ecb'),  # i with dot
            ('&#x323;', '\u0323'),  # lower dot
            ('&#x2c8;', '\u02c8'),
            ('&#x2cc;', '\u02cc')]

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
            chr(8217), "&rsquo;").replace(
            chr(660), "&#x294;")
