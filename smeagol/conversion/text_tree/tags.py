from .node import Node


class Tags:
    def __init__(self):
        self.state: str = None
        self.root = Node()
        self.open_tags = []
        self.closing_tags = []

    @property
    def opening_tags(self):
        return self.open_tags[-1]
    
    @property
    def current(self):
        try:
            return self._current
        except AttributeError:
            return self.root

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
            if len(self.opening_tags) >= (len(self.closing_tags) + 1):
                self.opening_tags[-1].name = tag
                self.remove_last_opener()

    def remove_last_opener(self):
        try:
            self.opening_tags.pop()
        except IndexError:
            self.open_tags.pop()
            self.opening_tags = self.open_tags[-1]

    def tagon(self, name: str):
        tag = self.new(name)
        self.current.add(tag)
        self.opening_tags.append(tag)
        self._current = tag

    def tagoff(self, name: str) -> None:
        self.closing_tags.append(name)
        self._current = self.current.parent

    def text(self, text: str):
        self.current.add(text)
