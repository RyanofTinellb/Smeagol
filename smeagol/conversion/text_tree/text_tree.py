from smeagol.conversion.text_tree.node import Node

class TextTree:
    'To replace "Tagger.show_tags()"'
    def __init__(self, text: list[tuple]):
        self._state:str = None
        self.current_node = Node()
        self.open_tags:list[list[Node]] = []
        self.new_opening_tags()
        self.closing_tags = []
        for elt in text:
            self._retag(*elt)
        if self._state == 'tagoff':
            self.rationalise()
    
    def __str__(self):
        return ''.join([str(elt) for elt in self.current_node])
        
    def new_opening_tags(self):
        self.opening_tags: list = []
        self.open_tags.append(self.opening_tags)

    def _retag(self, key: str, value: str, _=None) -> None:
        self.update_state(key)
        match key:
            case 'tagon':
                self._tagon(value)
            case 'text':
                self._text(value)
            case 'tagoff':
                self._tagoff(value)
            case _:
                pass

    def _tagon(self, name: str) -> None:
        tag = Node(self.current_node, name)
        self.current_node += tag
        self.current_node = tag
        self.opening_tags.append(tag)

    def _tagoff(self, name: str) -> None:
        self.closing_tags.append(name)
        self.current_node = self.current_node.parent

    def _text(self, text: str) -> None:
        self.current_node += text
    
    def update_state(self, new_state: str) -> None:
        if new_state not in ['tagon', 'tagoff', 'text']:
            return
        if new_state == self._state:
            return
        if self._state == 'tagoff':
            self.rationalise()
        if new_state == 'tagon':
            self.new_opening_tags()
        self._state = new_state
    
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


