import re
from itertools import cycle
from smeagol.widgets.styles.styles import Styles
from smeagol.editor.interface.template.props import Props

class Template:
    def __init__(self, filename, templates):
        template = templates.load(filename)
        self.text = template.get('text', [])
        self.styles = Styles({})
        self.templates = templates
        self.filename = filename
        self.props = Props()

    def replace_tags(self, text):
        return ''.join([self._replace(line, index) for index, line in enumerate(text)])

    def _replace(self, line, line_number=0):
        if line_number:
            self.props.starting = self.props.ending = True
        line = self._join(self._split(line))
        separator = self._separator_end() if self.props.ending else ''
        return f'{line}{separator}'

    def _split(self, line):
        return re.split('[<>]', line)

    def _join(self, line):
        return ''.join([f(x) for f, x in zip(cycle([self._text, self._tag]), line)])

    def _text(self, text):
        if not text:
            return ''
        if self.props.replace:
            return self.templates[text].html(self.props)
        if self.props.starting:
            return self._separator_start(text)
        return text

    def _tag(self, tag):
        fn = self._tagoff if tag.startswith('/') else self._tagon
        return fn(self.styles[tag.removeprefix('/')])

    def _tagon(self, tag):
        if tag.template:
            self.props.replace = True
            return ''
        if self.props.starting and not tag.block:
            return self._separator_start(tag.start)
        if tag.block:
            self.props.blocks.append(tag.separator)
        return f'{tag.start}'

    def _separator_start(self, text=''):
        self.props.starting = False
        separator = f'<{self.props.separator}>' if self.props.separator else ''
        return f'{separator}{text}'

    def _tagoff(self, tag):
        if tag.template:
            self.props.replace = False
        if self.props.ending and tag.block:
            return self._separator_end(tag.end)
        if tag.block:
            self.props.blocks.pop()
        return f'{tag.end}'

    def _separator_end(self, text='\n'):
        self.props.ending = False
        separator = f'</{self.props.separator}>' if self.props.separator else ''
        return f'{separator}{text}'

    def html(self, props):
        self.props = props
        return self.replace_tags(self.text)
