import random


class RandomWords:
    def __init__(self):
        self.geminate = 2

    @property
    def word(self):
        return ''.join(self.syllables)

    @property
    def consonant(self):
        lst = ['b', 'g', 'j', 'f', 'h', 'd', 'p', 'r', 't', 'm',
               'c', 'x', 'q', 'n', 'k', 'l', '’', 's']
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
        return random.choices(lst, scale)[0]

    @property
    def syllable(self):
        return self.consonant + self.vowel

    def double(self, syllable, num):
        consonant, vowel = syllable
        if num and not random.randint(0, self.geminate):
            if consonant == '’':
                return f'ʔ{vowel}'
            return consonant + syllable
        return syllable


creator = RandomWords()
for j in range(25):
    print(creator.word)
