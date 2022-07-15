import re
from itertools import cycle
from smeagol.conversion.api import Tagger


class Template(Tagger):
    def __init__(self, text, tags, templates):
        super().__init__(tags)
        self.text = text
        self.templates = templates
        self.starting = self.ending = False
        self.pipe = ''
        self.blocks = []
        self.replace = None

    @property
    def separator(self):
        return self.blocks[-1]

    def replace_tags(self, text):
        return ''.join([self._replace(line, index) for index, line in enumerate(text)])

    def _replace(self, line, line_number=0):
        if line_number:
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
        if self.replace:
            return self.templates[text].html(self.current)
        if self.starting:
            return self._separator_start(text)
        return text

    @property
    def current(self):
        return dict(
            starting=self.starting,
            ending=self.ending,
            blocks=self.blocks,
            pipe=self.pipe)

    @current.setter
    def current(self, values):
        values = values or {}
        self.starting = values.get('starting', False)
        self.ending = values.get('ending', False)
        self.blocks = values.get('blocks', [])
        self.pipe = values.get('pipe', '')


    def _tag(self, tag):
        fn=self._tagoff if tag.startswith('/') else self._tagon
        return fn(self.tags[tag.removeprefix('/')])

    def _tagon(self, tag):
        if tag.template:
            self.replace=True
            return ''
        elif self.starting and not tag.block:
            return self._separator_start(tag.start)
        elif tag.block:
            self.blocks.append(tag.separator)
        return f'{tag.start}'

    def _separator_start(self, text = ''):
        self.starting=False
        separator=f'<{self.separator}>' if self.separator else ''
        return f'{separator}{text}'

    def _tagoff(self, tag):
        if tag.template:
            self.replace=False
        if self.ending and tag.block:
            return self._separator_end(tag.end)
        if tag.block:
            self.blocks.pop()
        return f'{tag.end}'

    def _separator_end(self, text = '\n'):
        self.ending=False
        separator=f'</{self.separator}>' if self.separator else ''
        return f'{separator}{text}'

    def html(self, current = None):
        self.current = current
        return self.replace_tags(self.text)
