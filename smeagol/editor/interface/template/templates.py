import tkinter as tk
from smeagol.utilities import filesystem as fs
from smeagol.conversion import api as conversion
from .template import Template


class Templates:
    def __init__(self, filenames=None):
        self.filenames = filenames or {}
        self.main = self._new('main')
        self.search = self._new('search')
        self.page404 = self._new('page404')
        self.wholepage = self._new('wholepage')
        sections = self.filenames.get('sections', {})
        self.sections = {section: self._load(filename) for section, filename in sections.items()}

    @property
    def items(self):
        return self.templates.items
    
    @property
    def templates(self):
        return dict(main=self.main,
                    search=self.search,
                    page404=self.page404,
                    wholepage=self.wholepage,
                    **self.sections)
    
    def set_data(self, entry, styles):
        template = dict(text=entry.text, tagger=styles)
        self.sections['contents'] = self._open(template)
    
    def __getitem__(self, key):
        return self.sections[key]
    
    def _new(self, name):
        return self._open(self.filenames.get(name, ''))
    
    def _open(self, filename):
        return Template(filename, self)

    def load(self, filename):
        if not filename:
            return None
        return fs.load_yaml(filename)
        