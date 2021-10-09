from ...utilities import utils
import re
from itertools import cycle

class Tagger:
    def _text(self, text):
        return 'text', text, None

    def _tag(self, text):
        if text.startswith('/'):
            tag = self.tags.pop()
            return ('text', f'<{text}>', None) if ' ' in tag else ('tagoff', text[1:], None)
        self.tags.append(text)
        return ('text', f'<{text}>', None) if ' ' in text else ('tagon', text, None)

    def hide_tags(self, text):
        self.tags = []
        return self._hidetags(text)
    
    def _splittags(self, text):
        print(text)
        return re.split('[<>]', text)
    
    def _mutatetags(self, text):
        return [f(x) for f, x in zip(cycle([self._text, self._tag]), text)]
    
    @property
    def _hidetags(self):
        return utils.compose(self._splittags, self._mutatetags)
    
    def _retag(self, key, value, index):
        match key:
            case 'tagon':
                return self._tagon(value)
            case 'text':
                return self._text(value)
            case 'tagoff':
                return self._tagoff(value)
            case default:
                return ''
        
    def _untag(self, tag):
        return f'</{tag}>'
    
    def show_tags(self, text):
        self.tags = []
        try:
            text = ''.join([self._retag(*elt) for elt in text])
        except TypeError:
            raise TypeError(text)
        self.tags.reverse()
        text += ''.join([self._untag(tag) for tag in self.tags])
        return text
    
    def add_line_breaks(self, text):
        return [self._break(line) for line in text]
    
    def _break(self, line):
        return line if line.endswith('\n') else f'{line}\n'