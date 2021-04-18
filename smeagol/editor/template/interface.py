from ...widgets.styles import Styles
from ... import filesystem as fs

class Interface:
    def __init__(self, filename=None, optional=True):
        self.filename = filename
        self.optional = optional
        self.edited = False
        self._loaded = False

    def __setattr__(self, attr, value):
        if attr == 'text' and isinstance(value, list):
            self.template['template'] = value
        elif attr == 'styles' and isinstance(value, Styles):
            self.template['styles'] = dict(value.items())
        elif attr == 'filename' and self._loaded:
            self.load_template()
        super().__setattr__(attr, value)
    
    def __getattr__(self, attr):
        if attr in ('template', 'text', 'styles'):
            self.load_template()
            return getattr(self, attr)
        
    def copy(self):
        return Interface(self.filename, self.optional)
    
    def load_template(self):
        self.template = fs.load(self.filename)
        self.text = self.template['template']
        self.styles = Styles(self.template['styles'])
        self._loaded = True
    
    def save(self, text):
        self.text = self.styles.show_tags(text)
        fs.save(self.template, self.filename)