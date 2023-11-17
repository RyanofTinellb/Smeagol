import random

from ...conversion import api as conversion
from .highlulani import HighLulani


class DemoticLulani:
    def __init__(self):
        self.name = 'Demotic Lulani'
        self.lulani = HighLulani()
        self.demotic = conversion.HighToDemoticLulani()
        
    @property
    def word(self):
        return self.demotic.evolve(self._word)[-1]

    @property
    def _word(self):
        num = random.randint(0, 6)
        return f'{self.lulani_word}{self.lulani_word}' if num < 2 else self.lulani_word

    @property
    def lulani_word(self):
        return self.lulani.word
