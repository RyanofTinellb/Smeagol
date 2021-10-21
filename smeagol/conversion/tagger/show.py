from .tagger import Tagger

class Show(Tagger):
    def restore_tags(self, text):
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