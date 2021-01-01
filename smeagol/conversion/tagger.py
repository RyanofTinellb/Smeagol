import re
import json
from .. import utils
from itertools import cycle

class Tagger:
    def _text(self, text):
        return 'text', text, None

    def _tag(self, text):
        if text.startswith('/'):
            tag = self.tags.pop()
            return ('text', f'<{text}>', None) if ' ' in tag else ('tagoff', text[1:], None)
        else:
            self.tags.append(text)
            return ('text', f'<{text}>', None) if ' ' in text else ('tagon', text, None)

    def hide_tags(self, text):
        self.tags = []
        text = re.split('[<>]', text)
        text = [f(x) for f, x in zip(cycle([self._text, self._tag]), text)]
        return text
    
    def _retag(self, key, value, index):
        if key == 'tagon' and value != 'sel':
            self.tags.append(value)
            return f'<{value}>'
        elif key == 'text':
            return value
        elif key == 'tagoff' and value != 'sel':
            return self._untag(self.tags.pop())
        else:
            return ''
        
    def _untag(self, tag):
        return f'</{tag}>'
    
    def show_tags(self, text):
        with utils.ignored(TypeError):
            text = json.loads(text[1:])
        self.tags = []
        try:
            text = ''.join([self._retag(*elt) for elt in text])
        except TypeError:
            raise TypeError(text)
        self.tags.reverse()
        text += ''.join([self._untag(tag) for tag in self.tags])
        return text