from smeagol.conversion.text_tree.node import Node
from smeagol.utilities import utils


class Tags:
    def __init__(self, ranks=None):
        self.rank = ranks or {}
        self.current = None
        self.state: str = None
        self.root = Node()
        self.open_tags = []
        self.closing_tags = []

    @property
    def opening_tags(self):
        return self.open_tags[-1]

    @property
    def current(self):
        return self._current or self.root

    @current.setter
    def current(self, value):
        self._current = value

    def update_state(self, state: str) -> None:
        if state not in ['tagon', 'tagoff', 'text']:
            return
        if state == self.state:
            return
        if self.state == 'tagoff':
            self.rationalise()
        if state == 'tagon':
            self.open()
        self.state = state

    def open(self):
        tags: list = []
        self.open_tags.append(tags)
        return tags

    def new(self, name=None):
        return Node(self.current, name)

    def rationalise(self):
        while self.closing_tags:
            self._rationalise()

    def _rationalise(self):
        self.sort_closers()
        tag = self._rational_tag
        self.rename_opener(tag)
        try:
            self.closing_tags.remove(tag)
        except ValueError as e:
            raise ValueError(f'{tag} not found in {self.closing_tags} '
                             f'/ {self.open_tags}') from e
        self.remove_opener()

    def sort_closers(self):
        if len(self.opening_tags) >= len(self.closing_tags):
            self.closing_tags.sort(key=self._rank)

    def _rank(self, tag):
        tag, _lang = utils.try_split(tag)
        return self.rank.get(tag, 0)

    @property
    def _rational_tag(self):
        if len(self.opening_tags) >= len(self.closing_tags):
            return self.closing_tags[0]
        return self.opening_tags[-1].name

    def rename_opener(self, name):
        old_name = self.opening_tags[-1].name
        self.opening_tags[-1].name = name
        for tag in self.opening_tags:
            if tag.name == name:
                tag.name = old_name
                return

    def remove_opener(self):
        self.opening_tags.pop()
        if not self.opening_tags:
            self.open_tags.pop()

    def tagon(self, name: str):
        tag = self.new(name)
        self.current.add(tag)
        self.opening_tags.append(tag)
        self.current = tag

    def tagoff(self, name: str) -> None:
        self.closing_tags.append(name)
        self.current = self.current.parent

    def text(self, text: str):
        self.current.add(text)
