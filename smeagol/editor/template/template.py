class Template:
    def __init__(self, text, tagger, templates):
        self.tagger = tagger
        self.text = tagger.hide_tags(text)
        self.templates = templates
        self.replace = self.block = False
        self.tags = ['p']
    
    def expand(self, key='text', value='', _='', entry=None):
        tag = ''
        if key == 'tagon':
            if value == 'template':
                self.replace = True
            else:
                try:
                    style = self.tagger[value]
                except KeyError:
                    style = self.tagger.add(value)
                if style.block:
                    self.tags.append(style.block)
                if self.block and not style.block:
                    tag = f'<{style.block}>{style.start}'
                self.block = style.block
                return tag or style.start
        elif key == 'tagoff':
            if value == 'template':
                self.replace = False
            else:
                style = self.tagger[value]
                if style.block:
                    self.tags.pop()
                if not self.block and style.block:
                    tag = f'</{style.block}>{style.end}'
                self.block = style.block
                return tag or style.end
        elif key == 'text':
            if self.replace:
                value = value.replace('\n', '')
                return self.templates[value].html
            return value
        return ''

    @property
    def html(self):
        return ''.join([self.expand(*elt) for elt in self.text])