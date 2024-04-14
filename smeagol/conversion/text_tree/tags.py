from smeagol.conversion.text_tree.node import Node


class Tags:
    def __init__(self):
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
        while True:
            try:
                tag = self.closing_tags.pop(0)
            except IndexError:
                break
            if self._should_rationalise:
                self.opening_tags[-1].name = tag
            self.remove_last_opener()

    @property
    def _should_rationalise(self):
        # TODO: modify this based on a tag's ranks to prevent
        # <wordlist><block> and <block><wordlist> from being confused.
        return len(self.opening_tags) >= (len(self.closing_tags) + 1)

    def remove_last_opener(self):
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
