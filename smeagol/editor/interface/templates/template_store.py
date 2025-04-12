from dataclasses import dataclass

from smeagol.conversion.text_tree.text_tree import TextTree
from smeagol.editor.interface.assets.templates import Templates
from smeagol.editor.interface.templates.template import Template
from smeagol.utilities import filesystem as fs
from smeagol.utilities import utils
from smeagol.utilities.types import Entry
from smeagol.widgets.styles.styles import Styles


@dataclass
class Contents:
    page: Template = None
    contents: Entry = None

    def update(self, page=None, contents=None):
        if page:
            self.page = page
        if contents:
            self.contents = contents


class TemplateStore:
    def __init__(self, templates: Templates = None, links: dict = None, styles=None):
        self.started = utils.Flag()
        self.styles = styles
        self._contents = Contents()
        self._filenames = templates or Templates()
        self.links = links
        self._cache = {'sections': {}, 'special': {}}

    def special_files(self, site):
        for item in self._filenames.special:
            contents = self._get_from('special', item)
            self._contents.update(site, contents)
            yield item, self.main.html

    def __getattr__(self, attr):
        match attr:
            case 'main' | 'entry':
                return self._cached(attr)
            case 'page':
                return self._contents.page
            case 'contents':
                return self._contents.contents
            case 'entry_title':
                return self._contents.page.title
            case 'title':
                return self._contents.contents.title
            case 'sections' | 'special':
                return self._cache[attr]
            case _default:
                try:
                    return super().__getattr__(attr)
                except AttributeError as e:
                    name = type(self).__name__
                    raise AttributeError(
                        f"'{name}' object has no attribute '{attr}'") from e

    def __setattr__(self, attr, value):
        match attr:
            case 'page':
                self._contents.update(page=value)
            case _default:
                super().__setattr__(attr, value)


    def _cached(self, attr):
        try:
            return self._cache[attr]
        except KeyError:
            template = self._load(getattr(self._filenames, attr))
            return self._cache.setdefault(attr, template)

    def _load(self, filename):
        template = fs.load_yaml(filename)
        if not template:
            raise IOError(f'{filename} not found')
        styles = Styles(template.get('styles', {}))
        text = TextTree(template.get('text', []), styles.ranks)
        title = TextTree(template.get('title', []), styles.ranks)
        self._filenames.update(template.get('templates', {}))
        return Template(text, title, styles, self)

    def __getitem__(self, key):
        if key == 'main':
            return self._contents.contents
        return self._get_from('sections', key)

    def __setitem__(self, key, value):
        self.sections[key] = value

    def _get_from(self, name, item):
        try:
            return self._cache[name][item]
        except KeyError:
            template = self._load(getattr(self._filenames, name)[item])
            return self._cache[name].setdefault(item, template)

    def update(self, page):
        self._contents.update(page)

    def html(self, entry):
        self._contents.update(entry, self.entry)
        return self.main.html

    @property
    def items(self):
        return self.templates.items
