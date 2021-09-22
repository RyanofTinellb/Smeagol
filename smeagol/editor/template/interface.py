from ... import filesystem as fs
from ...widgets.styles import Styles
from .template import Template


class Interface:
    def __init__(self, filename=None, templates=None):
        self.templates = templates
        self.filename = filename
        if filename:
            template = fs.load(filename)
            try:
                text = '\n'.join(template['text'])
                tagger = Styles(template.get('tagger', {}))
            except (AttributeError, KeyError, TypeError) as e:
                raise e(f"Template file {filename} of wrong structure")
            self.template = Template(text, tagger, templates)
    
    def __str__(self):
        return self.filename
        
    @property
    def html(self):
        return self.template.html