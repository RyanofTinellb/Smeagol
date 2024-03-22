import re
from datetime import datetime as dt

from smeagol.utilities import utils
from smeagol.site.page.node import Node
from smeagol.conversion.text_tree.text_tree import TextTree


class Entry(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._texttree = None

    def __str__(self):
        return '\n'.join(self._text)

    def __hash__(self):
        return hash(tuple(self.location))

    def __getattr__(self, attr):
        match attr:
            case 'script' | 'id':
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
            case 'position' | 'script' | 'id':
                self._conditional_set(attr, value)
            case _default:
                super().__setattr__(attr, value)

    def _conditional_set(self, attr, value):
        if not value:
            return self.data.pop(attr, None)
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
        self.texttree, text = self._texts(value)
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
        except (ValueError, KeyError, TypeError):
            return dt.now()

    @date.setter
    def date(self, value):
        try:
            date = dt.strftime(value, '%Y-%m-%d')
        except (ValueError, KeyError):
            date = dt.strftime(dt.today(), '%Y-%m-%d')
        self.data['date'] = date

    def remove_script(self):
        self.data.pop('script', None)

    def replace(self, old, new):
        self.text = '\n'.join(self.text).replace(old, new)

    def regex_replace(self, pattern, repl):
        self.text = re.sub(pattern, repl, '\n'.join(self.text))

    def __getitem__(self, entry):
        if entry == '':
            return self
        count = 0
        try:
            page = self.eldest_daughter
        except AttributeError as e:
            raise KeyError(f'{self.name} has no children') from e
        try:
            while entry not in (page.name, page.id) and entry != count:
                page = page.next()
                count += 1
        except (IndexError, StopIteration) as e:
            raise KeyError(entry) from e
        return page

    def __eq__(self,  other):
        try:
            return self.name == other.name
        except AttributeError:
            return self == self.new(other.location)

    @property
    def list(self):
        if self.is_root:
            return []
        return [x.name for x in self.lineage][1:]

    @property
    def folder(self):
        return '/'.join(self.iterfolder)

    @property
    def iterfolder(self):
        for ancestor in self.ancestors:
            yield ancestor.url
        if not self.is_root and not self.is_leaf:
            yield self.url

    def hyperlink(self, destination, template='{0}', anchors=True):
        try:
            if self == destination:
                return template.format(self.name)
            address, link = self._direct(destination, template)
        except AttributeError:  # destination is a string
            address, link = self._indirect(destination, template)
        return link if anchors else address

    def _indirect(self, destination, template):
        up = self.level + int(self.has_children) - 1
        address = (up * '../') + destination
        destination = template.format(destination)
        link = f'<a href="{address}">{destination}</a>'
        return address, link

    def _direct(self, destination, template):
        if self.related_to(destination):
            up = self.level - destination.level
        else:
            up = self.distance(destination)
        up -= int(self.is_leaf)
        urls = [entry.url for entry in destination.unique_lineage(self)]
        if destination.has_children:
            urls[-1] = 'index'
        down = '/'.join(urls)
        address = (up * '../') + down + '.html'
        destination = template.format(destination.name)
        link = f'<a href="{address}">{destination}</a>'
        return address, link

    @property
    def title(self):
        return utils.remove_text(r'[\[<].*?[\]>]', [self.name])[0]

    def heading(self, name, level=1):
        return f'<h{level}>{name}</h{level}>'

    @property
    def title_heading(self):
        return self.heading(self.name)

    @property
    def wholepage_heading(self):
        return self.heading(self.name, self.level)

    @property
    def wholepage(self):
        return f'{self.wholepage_heading} {self.wholepage_contents}<p></p>'

    @property
    def category_title(self):
        titles = [self.title, self.matriarch.title]
        if self.level < 2:
            return self.title
        if self.ancestor(2).name == 'Sample Texts':
            return '{0} - Sample Text in {1}'.format(*titles)
        return '{1} {0}'.format(*titles)

    def story_title(self, story_name):
        return ' &lt; '.join(self._story_title(story_name))

    def _story_title(self, story_name):
        if not self.level:
            return [story_name]
        if self.level == 1:
            return [self.title, story_name]
        return [self.title, self.matriarch.title, story_name]

    @property
    def toc(self):
        if self.is_root or self.is_leaf:
            return ''
        links = '\n'.join(
            [f'<p>{self.hyperlink(d)}</p>' for d in self.daughters])
        return ('<div class="toc">\n'
                f'{links}\n'
                '</div>')
