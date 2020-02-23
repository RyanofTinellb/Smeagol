import re
import json
from itertools import cycle
from contextlib import contextmanager

from ..widgets import Style
from ..utils import ignored


class Tagger:
    def __init__(self, styles=None):
        styles = styles or {}
        with ignored(TypeError):
            styles = json.loads(styles)
        self.styles = {'default': Style(name='default')}
        if isinstance(styles, self.__class__):
            self.styles.update({n: s.copy() for n, s in styles.styles.items()})
        else:
            self.styles.update({n: Style(name=n, **s) for n, s in styles.items()})

    def __contains__(self, item):
        return item in self.styles
    
    def __iter__(self):
        return iter(self.styles.values())
    
    def __getitem__(self, name):
        return self.styles[name]
    
    def __setitem__(self, name, value):
        self.styles[name] = value

    def copy(self):
        return Tagger(self)
    
    @property
    def names(self):
        return list(self.styles.keys())
    
    def update(self, styles):
        self.styles = styles.styles

    def add(self, style):
        try:
            self.styles[style.name] = style
        except AttributeError:
            self.styles[style] = Style(name=style)
    
    def remove(self, style):
        try:
            del self.styles[style]
        except KeyError:
            self.styles = {n: s for n, s in self.styles.items() if s != style}
    
    def show_tags(self, text):
        '''text is formatted'''
        with ignored(TypeError):
            text = json.loads(text[1:])
        self.tags = []
        text = ''.join([self._retag(*elt) for elt in text])
        self.tags.reverse()
        text += ''.join([self._untag(tag) for tag in self.tags])
        return text
    
    def _retag(self, key, value, index):
        if key == 'tagon' and value != 'sel':
            self.tags.append(value)
            return f'<{value}>'
        elif key == 'text':
            return value
        elif key == 'tagoff' and value != 'sel':
            value = self.tags.pop()
            return f'</{value}>'

    def _untag(self, tag):
        return f'</{tag}>'

    def hide_tags(self, text):
        text = re.split('[<>]', text)
        text = [f(x) for f, x in zip(cycle([self._text, self._tag]), text)]
        return f'\x08{json.dumps(text, indent=2)}'
    
    def _tag(self, text):
        if text.startswith('/'):
            return 'tagoff', text[1:], None
        else:
            return 'tagon', text, None

    def _text(self, text):
        return 'text', text, None
    
    def expand_tags(self, text):
        for style in self:
            start, end = style.tags
            if style.language:
                def _lang(regex, tag=start):
                    return tag.replace('>', f' lang="x-tlb-{regex.group(1)}">')
                text = re.sub(fr'<{style.name}-(.*?)>', _lang, text)
                text = re.sub(fr'</{style.name}-(.*?)>', end, text)
            else:
                text = text.replace(f'<{style.name}>', start)
                text = text.replace(f'</{style.name}>', end)
        return text