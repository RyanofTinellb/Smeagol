from datetime import datetime as dt

from smeagol.utilities import utils
from smeagol.site.page.relation import Relation
from smeagol.conversion.text_tree.text_tree import TextTree


class Entry(Relation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._texttree = None

    def __str__(self):
        return '\n'.join(self._text)

    def __getattr__(self, attr):
        match attr:
            case 'script' | 'id' | 'title':
                return self.data.get(attr, '')
            case 'position':
                return self.data.get(attr, '1.0')
            case _default:
                try:
                    return super().__getattr__(attr)
                except AttributeError as e:
                    name = self.__class__.__name__
                    raise AttributeError(
                        f"'{name}' object has no attribute '{attr}'") from e

    def __setattr__(self, attr, value):
        match attr:
            case 'position' | 'script' | 'id' | 'title':
                self._conditional_set(attr, value)
            case _default:
                super().__setattr__(attr, value)

    def _conditional_set(self, attr, value):
        if not value:
            return self.data.pop(attr)
        self.data[attr] = value
        return None

    @property
    def _text(self):
        return self.data.get('text', [])

    @property
    def text(self):
        if not self._texttree:
            self._texttree = TextTree(self._text)
        return self._texttree

    @text.setter
    def text(self, value):
        self._texttree, text = self._texts(value)
        with utils.ignored(AttributeError):
            text = [line for line in text.splitlines() if line]
        self.data['text'] = text

    def _texts(self, value):
        if isinstance(value, TextTree):
            return value, str(value)
        return TextTree(value), value

    @property
    def date(self):
        try:
            date = self.data.get('date')
            return dt.strptime(date, '%Y-%m-%d')
        except (TypeError, KeyError):
            return dt.now()

    def update_date(self, value=None):
        try:
            date = dt.strftime(value, '%Y-%m-%d')
        except (ValueError, KeyError, TypeError):
            date = dt.strftime(dt.today(), '%Y-%m-%d')
        self.data['date'] = date
