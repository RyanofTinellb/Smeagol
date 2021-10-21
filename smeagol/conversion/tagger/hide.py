import re
from itertools import cycle
from .tagger import Tagger

class Hide(Tagger):
    def replace_tags(self, text):
        return self._flatten([self._remove(line) for line in text])
    
    def _flatten(self, obj):
        return [item for sublist in obj for item in sublist if item]
    
    def _remove(self, line):
        line = self._join(self._split(line + '\n'))
        return line
    
    def _split(self, line):
        return re.split('[<>]', line)
    
    def _join(self, line):
        return [f(x) for f, x in zip(cycle([self._text, self._tag]), line)]
    
    def _text(self, text):
        return ('text', text) if text else None
    
    def _tag(self, tag):
        status = 'off' if tag.startswith('/') else 'on'
        return (f'tag{status}', tag.replace('/', ''))