from random import *

class RandomWords():
    def __init__(self, number, geminate):
        self.maximum = number
        self.geminate = geminate - 1

    @property
    def words(self):
        return [self.word() for x in range(self.maximum)]

    def __iter__(self):
        return self

    def consonant(self):
        lst = ['b', 'g', 'j', 'f', 'h', 'd', 'p', 'r', 't', 'm', 'c', 'x', 'q', 'n', 'k', 'l', unichr(8217), 's']
        scale = [10, 10, 11, 12, 13, 14, 15, 16, 17, 19, 21, 24, 27, 32, 38, 47, 62, 82]
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
            output = map(lambda x: x <= randint(1, sum(scale)), output).index(False) - 1
            output = lst[output]
        except ValueError:
            output = lst[-1]
        return output

    def syllable(self):
        return self.consonant() + self.vowel()

    def word(self):
        return ''.join([self.double(self.syllable(), i) for i in range(self.numsyllables())])

    def double(self, syllable, num):
        consonant, vowel = list(syllable)
        if num and not randint(0, self.geminate):
            return consonant + syllable if consonant != unichr(8217) else unichr(660) + vowel
        else:
            return syllable
