class Template:
    def __init__(self, name='', page=None, styles=None, templates=None):
        self.name = name
        self.page = page or {}
        self.styles = styles
        self.templates = templates or Templates()
        self.replace = self.block = False
        self.tags = ['p']
    
    def expand(self, key='text', value='', _=''):
        tag = ''
        if key == 'tagon':
            if value == 'template':
                self.replace = True
            else:
                style = self.styles[value]
                if style.tag:
                    self.tags.append(style.tag)
                if self.block and not style.block:
                    tag = f'<{style.tag}>{style.start}'
                self.block = style.block
                return tag or style.start
        elif key == 'tagoff':
            if value == 'template':
                self.replace = False
            else:
                style = self.styles[value]
                if style.tag:
                    self.tags.pop()
                if not self.block and style.block:
                    tag = f'</{style.tag}>{style.end}'
                self.block = style.block
                return tag or style.end
        elif key == 'text':
            if self.replace:
                value = value.replace('\n', '')
                return self.templates[value].html
            return value

    @property
    def html(self):
        return ''.join([self.expand(*elt) for elt in self.page])


class Templates:
    def __init__(self, templates=None):
        self.templates = templates or {}

    def html(self, entry):
        return self.templates['template'].html