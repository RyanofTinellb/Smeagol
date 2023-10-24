class TextDump:
    'To replace "Tagger.show_tags()"'
    def __init__(self, text: list[tuple]):
        self._state:str = None
        self.open_tags:list[list[list]] = []
        self.new_opening_tags()
        self.closing_tags = []
        self.contents = self._contents(text)
        if self._state == 'tagoff':
            self.rationalise()
    
    def _contents(self, text):
        return [self._retag(*elt) for elt in text]
        
    def new_opening_tags(self):
        self.opening_tags: list = []
        self.open_tags.append(self.opening_tags)

    def _retag(self, key: str, value: str, _=None) -> None:
        self.update_state(key)
        match key:
            case 'tagon':
                return self._tagon(value)
            case 'text':
                return self._text(value)
            case 'tagoff':
                return self._tagoff(value)
            case other:
                return [other, value] 

    def _tagon(self, name: str) -> None:
        tag = ['tagon', name]
        self.opening_tags.append(tag)
        return tag

    def _tagoff(self, name: str) -> None:
        tag = ['tagoff', name]
        self.closing_tags.append(tag)
        return tag

    def _text(self, text: str) -> None:
        return ['text', text]
    
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
            print(self.open_tags)
            print(self.opening_tags)
            print(self.closing_tags)
            print()
            try:
                tag = self.closing_tags.pop(0)
            except IndexError:
                break
            self.rename(self.opening_tags[-1], tag, self.choose_precedence())
            self.remove_last_opener()
    
    def choose_precedence(self):
        return len(self.opening_tags) > (len(self.closing_tags) + 1)
    
    def rename(self, opener, closer, precedence):
        if precedence:
            closer[1] = opener[1]
            return
        opener[1] = closer[1]
        return
    
    def remove_last_opener(self):
        try:
            self.opening_tags.pop()
        except IndexError:
            self.open_tags.pop()
            self.opening_tags = self.open_tags[-1]


