import re
from itertools import cycle

from .tag import Tag


def name(tag):
    return tag.get('tags', {}).get('name', '')


class Tagger:
    def __init__(self, tags):
        self.tags = {name(tag): self.create_tag(rank, tag)
                    for rank, tag in enumerate(tags)}

    @staticmethod
    def create_tag(rank=0, tag=None):
        tag = tag or {}
        return Tag(rank, **tag)

    '''Show Tags: transform a Tkinter dump into a list of strings'''

    def show_tags(self, text: list[tuple]) -> list[str]:
        print(text)
        self.open_tags = []
        self.to_open = []
        return self._show(text).splitlines()

    def _show(self, text):
        return ''.join([self._retag(*elt) for elt in text])

    def _retag(self, key, text, index=0):
        match key:
            case 'tagon':
                return self._tagon(text)
            case 'text':
                return self._text(text)
            case 'tagoff':
                return self._tagoff(text)
            case default:
                return ''

    def _tagon(self, tag):
        for obj in self.open_tags, self.to_open:
            self._add_to(obj, tag)
        return ''

    def _add_to(self, obj, tag):
        obj.append(self.tags[tag])
        obj.sort(key=lambda x: x.rank)

    def _tagoff(self, tag):
        return f'</{self.open_tags.pop().name}>'

    def _text(self, text):
        tags = ''.join([f'<{tag.name}>' for tag in self.to_open])
        self.to_open = []
        return f'{tags}{text}'

    '''Hide Tags: transform a list of strings into something suitable for textboxes'''

    def hide_tags(self, text):
        return self._flatten([self._remove(line) for line in text])

    def _flatten(self, obj):
        return [item for sublist in obj for item in sublist if item]

    def _remove(self, line):
        line = self._join(self._split(line + '\n'))
        return line

    def _split(self, line):
        return re.split('[<>]', line)

    def _join(self, line):
        return [f(x) for f, x in zip(cycle([self._text_tuple, self._tag]), line)]

    def _text_tuple(self, text):
        return ('text', text) if text else None

    def _tag(self, tag):
        status = 'off' if tag.startswith('/') else 'on'
        return (f'tag{status}', tag.replace('/', ''))
