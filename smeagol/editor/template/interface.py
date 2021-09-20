from ... import filesystem as fs
from ...widgets.styles import Styles
from .template import Template


class Interface:
    def __init__(self, filename=None, optional=True, templates=None):
        self.templates = templates
        self.filename = filename
        self.optional = optional
        if filename:
            template = fs.load(filename)
            try:
                text = '\n'.join(template['text'])
                tagger = Styles(template.get('tagger', {}))
            except (AttributeError, KeyError, TypeError):
                print(f"Template file {filename} of wrong structure")
            self.template = Template(text, tagger, templates)
        
    @property
    def html(self):
        try:
            return self.template.html
        except KeyError:
            print(self.filename)
            raise