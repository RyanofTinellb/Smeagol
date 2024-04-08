import re

from smeagol.conversion.text_tree.tags import Tags
from smeagol.utilities import utils


class TextTree(Tags):
    def __init__(self, text):
        super().__init__()
        try:
            self.process_strings(text)
        except TypeError:
            self.process_tuples(text)
        if self.state == 'tagoff':
            self.rationalise()

    @property
    def name(self):
        return ''

    def __iter__(self):
        return iter(self.root)

    def __str__(self):
        return str(self.root)

    def pprint(self):
        self.root.pprint()

    def process_tuples(self, text: list[tuple]):
        self.retag_tuples(text)

    def retag_tuples(self, text):
        for elt in text:
            self._retag(*elt)

    def process_strings(self, text: list[str]):
        for line in text:
            self._retag_line(line + '\n')

    def _retag_line(self, line):
        line = re.split('[<>]', line)
        utils.alternate([self._text, self._tag], line)
        # self._text('\n')

    def _text(self, text):
        self._retag('text', text)

    def _tag(self, tag):
        status = 'off' if tag.startswith('/') else 'on'
        self._retag(f'tag{status}', tag.removeprefix('/'))

    def _retag(self, key: str, value: str, _index=None) -> None:
        if not value:
            return
        self.update_state(key)
        match key:
            case 'tagon':
                self.tagon(value)
            case 'text':
                self.text(value)
            case 'tagoff':
                self.tagoff(value)
            case _:
                pass
