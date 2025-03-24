from smeagol.conversion.text_tree.text_tree import TextTree
from smeagol.editor.interface.assets.templates import Templates
from smeagol.editor.interface.templates.template import Template
from smeagol.utilities import filesystem as fs
from smeagol.utilities import utils
from smeagol.utilities.types import Page
from smeagol.widgets.styles.styles import Styles


class TemplateStore:
    def __init__(self, templates: Templates = None, links: dict = None, entry_styles = None):
        self.started = utils.Flag()
        self.entry_styles = entry_styles
        self.page = self.styles = None
        self._filenames = templates or Templates()
        self.links = links
        self._cache = {'sections': {}}

    def __getattr__(self, attr):
        match attr:
            case 'main' | 'search' | 'page404':
                return self._cached(attr)
            case 'wholepage':
                return self._cached(attr, wholepage=True)
            case 'sections':
                return self._cache['sections']
            case _default:
                try:
                    return super().__getattr__(attr)
                except AttributeError as e:
                    name = type(self).__name__
                    raise AttributeError(
                        f"'{name}' object has no attribute '{attr}'") from e

    def _cached(self, attr, wholepage=False):
        try:
            return self._cache[attr]
        except KeyError:
            template = self._load(getattr(self._filenames, attr))
            template.components.wholepage = wholepage
            return self._cache.setdefault(attr, template)

    def _load(self, filename):
        template = fs.load_yaml(filename)
        styles = Styles(template.get('styles', {}))
        text = TextTree(template.get('text', []), styles.ranks)
        self._filenames.update(template.get('templates', {}))
        return Template(text, styles, self)

    def __getitem__(self, key):
        try:
            return self.sections[key]
        except KeyError:
            template = self._load(self._filenames.sections[key])
            return self.sections.setdefault(key, template)

    def __setitem__(self, key, value):
        self.sections[key] = value

    @property
    def items(self):
        return self.templates.items

    def set_data(self, page: Page = None, styles: Styles = None):
        self.page = page or self.page
        self.styles = styles or self.styles or self.entry_styles
