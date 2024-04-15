from smeagol.conversion.text_tree.text_tree import TextTree
from smeagol.editor.interface.assets.templates import Templates
from smeagol.editor.interface.templates.flag import Flag
from smeagol.editor.interface.templates.template import Template
from smeagol.utilities import filesystem as fs
from smeagol.utilities.types import Page
from smeagol.widgets.styles.styles import Styles


class TemplateStore:
    def __init__(self, templates: Templates = None):
        self.started = Flag()
        templates = templates or Templates()
        self.main = self._load(templates.main)
        self.search = self._load(templates.search)
        self.page404 = self._load(templates.page404)
        self.wholepage = self._load(templates.wholepage)
        sections = templates.sections
        self.sections = {section: self._load(
            filename) for section, filename in sections.items()}

    @property
    def items(self):
        return self.templates.items

    @property
    def templates(self):
        return {'main': self.main,
                'search': self.search,
                'page404': self.page404,
                'wholepage': self.wholepage,
                **self.sections}

    def set_data(self, page: Page, styles: Styles):
        self.sections['contents'] = Template(page.text, styles, self)

    def __getitem__(self, key):
        try:
            return self.sections[key]
        except KeyError as e:
            name = type(self).__name__
            raise KeyError(f'{name} object has no item {key}') from e

    def __setitem__(self, key, value):
        self.sections[key] = value

    def _load(self, filename):
        template = fs.load_yaml(filename)
        try:
            styles = Styles(template.get('styles', {}))
        except AttributeError as e:
            raise AttributeError(f'{filename} is badly formatted. '
                                 'Please make a note of it.') from e
        try:
            text = TextTree(template.get('text', []), styles.ranks)
        except ValueError as e:
            raise ValueError(f'{filename} is badly formatted. '
                                 'Please make a note of it.') from e        
        return Template(text, styles, self)
