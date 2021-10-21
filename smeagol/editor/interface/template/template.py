from ....conversion.api import Tagger

class Template(Tagger):
    def __init__(self, text, tags, templates):
        super().__init__(self, tags)
        self.text = text
        self.templates = templates
        self.text = self.hide_tags(text)
        self.replace = self.block = False
    
    def expand(self):
        return self.hide
    
    @property
    def html(self):
        return ''.join([self.expand(*elt) for elt in self.text])