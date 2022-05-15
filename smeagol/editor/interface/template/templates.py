import tkinter as tk
from ....utilities import filesystem as fs
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
        self.sections = {section: self._load(filename) for section, filename in sections.items()}
    
    def set_data(self, entry, styles):
        template = dict(text=entry.text, tagger=styles)
        self.sections['contents'] = self._open(template)
    
    def __getitem__(self, key):
        return self.sections[key]
    
    def _new(self, name):
        return self._load(self.filenames.get(name, ''))
    
    def _load(self, filename):
        if not filename:
            return None
        template = fs.load(filename)
        # try:
        return self._open(template)
        # except (AttributeError, KeyError, TypeError) as e:
        #     raise e.__class__(f"Template file {filename} of wrong structure")
    
    def _open(self, template):
        # tk()
        text = '\n'.join(template['text'])
        tagger = widgets.Styles(template.get('styles', {}))
        return Template(text, tagger, self)