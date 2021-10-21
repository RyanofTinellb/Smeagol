import re
from itertools import cycle

from .tagger import Tagger


class Expand(Tagger):
    def __init__(self, tags):
        super().__init__(tags)
        self.starting = self.ending = False
        self.blocks = []
    
    @property
    def separator(self):
        return self.blocks[-1]

    def replace_tags(self, text):
        return ''.join([self._replace(line) for line in text])
    
    def _replace(self, line):
        self.starting = self.ending = True
        line = self._join(self._split(line))
        separator = self._separator_end() if self.ending else ''
        return f'{line}{separator}'
        
    def _split(self, line):
        return re.split('[<>]', line)
    
    def _join(self, line):
        return ''.join([f(x) for f, x in zip(cycle([self._text, self._tag]), line)])
    
    def _text(self, text):
        if not text:
            return ''
        if self.starting:
            return self._separator_start(text)
        return text
    
    def _tag(self, tag):
        fn = self._tagoff if tag.startswith('/') else self._tagon
        return fn(self.tags[tag.removeprefix('/')])
    
    def _tagon(self, tag):
        if self.starting and not tag.block:
            return self._separator_start(tag.start)
        if tag.block:
            self.blocks.append(tag.separator)
        return f'{tag.start}'

    def _separator_start(self, text=''):
        self.starting = False
        separator = f'<{self.separator}>' if self.separator else ''
        return f'{separator}{text}'

    def _tagoff(self, tag):
        if self.ending and tag.block:
            return self._separator_end(tag.end)
        if tag.block:
            self.blocks.pop()
        return f'{tag.end}'
    
    def _separator_end(self, text='\n'):
        self.ending = False
        separator = f'</{self.separator}>' if self.separator else ''
        return f'{separator}{text}'
