from collections import OrderedDict
from evolve import HighToVulgarLulani
import random
import json
import re


class RandomWords():
    def __init__(self, language=None):
        self.maximum = 20
        languages = OrderedDict()
        languages['en'] = English
        languages['hl'] = HighLulani
        languages['vl'] = VulgarLulani
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
        return [self.converter.word() for x in range(self.maximum)]

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
            'shortstories',
        ]
        for filename in filenames:
            with open(folder.format(filename)) as page:
                page = json.load(page)
            self.collate(page, self.words)
        self.words = list(self.words)

    def collate(self, page, words):
        words.update({word for line in page['text']
                for word in line.split()})
        for child in page.get('children', []):
            self.collate(child, self.words)

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
                r'&date=',
                r'\W|\d'
            ):
                choice = re.sub(sub, '', choice)
        return choice.lower()


class HighLulani:
    def __init__(self):
        self.name = 'High Lulani'
        self.geminate = 2

    def word(self):
        return u''.join([self.double(self.syllable(), i) for i in range(self.numsyllables())])

    def consonant(self):
        lst = ['b', 'g', 'j', 'f', 'h', 'd', 'p', 'r', 't', 'm',
               'c', 'x', 'q', 'n', 'k', 'l', unichr(8217), 's']
        scale = [10, 10, 11, 12, 13, 14, 15, 16,
                 17, 19, 21, 24, 27, 32, 38, 47, 62, 82]
        return self.pick(lst, scale)

    def vowel(self):
        lst = ['a', 'i', 'u']
        scale = [4, 2, 1]
        return self.pick(lst, scale)

    def numsyllables(self):
        lst = [1, 2, 3, 4]
        scale = [7, 18, 15, 2]
        return self.pick(lst, scale)

    @staticmethod
    def pick(lst, scale):
        try:
            output = map(lambda x: sum(scale[:x]), range(len(scale)))
            output = map(lambda x: x <= random.randint(
                1, sum(scale)), output).index(False) - 1
            output = lst[output]
        except ValueError:
            output = lst[-1]
        return output

    def syllable(self):
        return self.consonant() + self.vowel()

    def double(self, syllable, num):
        consonant, vowel = list(syllable)
        if num and not random.randint(0, self.geminate):
            return consonant + syllable if consonant != unichr(8217) else unichr(660) + vowel
        else:
            return syllable

class VulgarLulani:
    def __init__(self):
        self.name = 'Vulgar Lulani'
        self.lulani = HighLulani()
        self.vulgar = HighToVulgarLulani()
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
        word = self.lulani.word()
        return word.replace(
            unichr(8217), "&rsquo;").replace(
            unichr(660), "&#x294;")
