from ....utilities import utils, filesystem as fs
from ....widgets import api as widgets
from .template import Template


class Templates:
    def __init__(self, filenames=None):
        self.filenames = filenames or {}
        self.main = self._new('main')
        self.search = self._new('search')
        self.search = self._new('search404')
        self.wholepage = self._new('wholepage')
        sections = self.filenames.get('sections', {})
        self.sections = {section: self._open(filename) for section, filename in sections.items()}
    
    def __getitem__(self, key):
        return self.sections[key]
    
    def _new(self, name):
        return self._open(self.filenames.get(name, ''))
    
    def _open(self, filename):
        if not filename:
            return None
        template = fs.load(filename)
        try:
            text = '\n'.join(template['text'])
            tagger = widgets.Styles(template.get('tagger', {}))
        except (AttributeError, KeyError, TypeError) as e:
            raise e.__class__(f"Template file {filename} of wrong structure")
        return Template(text, tagger, self)