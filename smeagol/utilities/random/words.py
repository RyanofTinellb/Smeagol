from .demoticlulani import DemoticLulani
from .english import English
from .highlulani import HighLulani


class Words:
    def __init__(self, language='', samples=''):
        self.languages = {
            'en': (English, samples),
            'x-tlb-hl': (HighLulani,),
            'x-tlb-dl': (DemoticLulani,)
        }
        self.select(language)

    def select(self, language=''):
        language = language.lower()[:2]
        self.converter = self._converters(language)

    def _converters(self, language=''):
        language = language or next(iter(self.languages))
        try:
            converter, *args = self.languages[language]
        except (AttributeError, KeyError):
            converter, *args = next(iter(self.languages.values()))
        return converter(*args)

    @property
    def name(self):
        return self.converter.name

    def words(self, num):
        words = [self.converter.word for x in range(num)]
        return [word for word in words if word]

    def __iter__(self):
        return self
