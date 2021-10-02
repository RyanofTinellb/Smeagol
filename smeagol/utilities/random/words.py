from .english import English
from .highlulani import HighLulani
from .demoticlulani import DemoticLulani

class Words:
    def __init__(self, language=None, samples=''):
        self.languages = dict(
                              en=(English, samples),
                              hl=(HighLulani,),
                              dl=(DemoticLulani,)
                             )
        self.converter = self._converters(language)

    def _converters(self, language=None):
        language = language or next(iter(self.languages))
        try:
            converter, *args = self.languages[language]
        except AttributeError:
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