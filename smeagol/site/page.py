import os
import shutil
from uuid import uuid4 as uuid

from page_utils import *

from ..defaults import default
from ..conversion import *
from smeagol import utils
from .node import Node

markdown = Markdown()


class Page(Node):
    def __init__(self, tree=None, location=None):
        super().__init__(tree, location)

    def __hash__(self):
        return hash(tuple(self.location))

    def __getattr__(self, attr):
        if attr in {'name', 'script', 'id'}:
            return self.find().get(attr, '')
        elif attr in {'text'}:
            return self.find().get(attr, [])
        elif attr in {'position'}:
            return self.find().get(attr, '1.0')
        elif attr == 'date':
            try:
                date = self.find()['date']
                return dt.strptime(date, '%Y-%m-%d')
            except (ValueError, KeyError):
                return dt.now()
        elif attr in ('flatname', 'score'):
            try:
                key = 'name' if attr == 'flatname' else 'score'
                return self.find()['flatname'][key]
            except KeyError:
                self.refresh_flatname()
                return getattr(self, attr)
        else:
            return super().__getattr__(attr)

    def __setattr__(self, attr, value):
        if attr == 'text':
            with ignored(AttributeError):
                value = [_f for _f in value.split('[') if _f]
            self.find()['text'] = value
        elif attr in {'name', 'position', 'script', 'flatname', 'id'}:
            if value:
                self.find()[attr] = value
            else:
                self.find().pop(attr, None)
        else:
            super().__setattr__(attr, value)

    def __str__(self):
        return '['.join(self.text) # some pages are meant to start without a [

    def update_date(self):
        self.find()['date'] = dt.strftime(dt.today(), '%Y-%m-%d')

    def refresh_flatname(self):
        self.find()['flatname'] = self._flatname

    def remove_flatname(self):
        self.find().pop('flatname', None)

    def remove_script(self):
        self.find().pop('script', None)

    @property
    def link(self):
        link = self.folder
        url = self.url if not self.has_children else 'index'
        hyperlink = f'{link}/{url}' if link else url
        return hyperlink + '.html'

    @property
    def url(self):
        if self.location is None:
            return 'index'
        return urlform(self.name)

    @property
    def analysis(self):
        wordlist = {}
        content = [str(self)]
        # remove tags, and items between some tags
        change_text(
            r'\[\d\]|<(ipa|high-lulani|span).*?</\1>|<.*?>|^\d\]', ' ', content)
        # remove heading markers from tables
        remove_text(r'\|\w*', content)
        # change punctuation to paragraph marks, so that splitlines works
        change_text(r'[!?.|]', '\n', content)
        # change punctuation to space
        change_text(r'[_()]', ' ', content)
        # remove spaces at the beginnings and end of lines,
        #    duplicate spaces and end-lines
        remove_text(r'(?<=\n) +| +(?=[\n ])|^ +| +$|\n+(?=\n)|[,:]', content)
        # remove duplicate end-lines, and tags in square brackets
        remove_text(r'\n+(?=\n)|\[.*?\]', content)
        content = buyCaps(content[0])
        lines = content.splitlines()
        content = [markdown.to_markdown(content).lower()]
        change_text(r'&.*?;', ' ', content)
        # change punctuation, and tags in square brackets, into spaces
        change_text(r'\'\"|\[.*?\]|[!?`\"/{}\\;-]|\'($| )|\d', ' ', content)
        # make glottal stops lower case where appropriate
        change_text(r"(?<=[ \n])''", "'", content)
        for number, line in enumerate(content[0].splitlines()):
            for word in line.split():
                try:
                    if wordlist[word][-1] != number:
                        wordlist[word].append(number)
                except KeyError:
                    wordlist[word] = [number]
        return dict(words=wordlist,
                    sentences=lines)

    @property
    def _flatname(self):
        name = markdown.to_markdown(self.name)
        score = 0
        name = re.sub(double_letter, r'#\1', name)
        for points, pattern in enumerate(punctuation):
            score += score_pattern(name, pattern, radix, points + 1)
            name = re.sub('\\' + pattern, '', name)
        return dict(name=name, score=score)

    def __getitem__(self, entry):
        if entry == '':
            return self
        count = 0
        try:
            page = self.eldest_daughter
        except AttributeError:
            raise KeyError('{self.name} has no children')
        try:
            while entry not in (page.name, page.id) and entry != count:
                page = page.next()
                count += 1
        except (IndexError, StopIteration):
            raise KeyError(entry)
        return page

    def __eq__(self,  other):
        try:
            return self.name == other.name
        except AttributeError:
            return self == self.new(other.location)

    def __lt__(self, other):
        try:
            if self.flatname == other.flatname and self.score < other.score:
                return True
        except AttributeError:
            return self < self.new(other.location)
        for s, t in zip(self.flatname, other.flatname):
            if s != t:
                try:
                    return alphabet.index(s) < alphabet.index(t)
                except ValueError:
                    continue
        else:
            return len(self.name) < len(other.name)

    def __ne__(self, other):
        return not self == other

    def __ge__(self, other):
        return not self < other

    def __gt__(self, other):
        return self != other and self >= other

    def __le__(self, other):
        return self == other or self < other

    def sort(self, entry=None):
        if entry:
            ID = entry.id = str(uuid())
        self.children = [child.find() for child in sorted(self.daughters)]
        entry = self.root[ID]
        entry.id = ''
        return entry

    @asynca
    def publish(self, template=None):
        text = self.html(template)
        dumps(text, self.link)

    @property
    def list(self):
        if self.is_root:
            return []

        def name(x): return x.name
        return list(map(name, self.lineage))[1:]

    @property
    def folder(self):
        return '/'.join(self.iterfolder)

    @property
    def iterfolder(self):
        for ancestor in self.ancestors:
            yield ancestor.url
        if not self.is_root and not self.is_leaf:
            yield self.url
        return

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
        destination = template.format(buyCaps(destination.name))
        link = f'<a href="{address}">{destination}</a>'
        return address, link

    @property
    def title(self):
        return remove_text(r'[\[<].*?[\]>]', [buyCaps(self.name)])[0]

    @property
    def title_heading(self):
        return heading(buyCaps(self.name))
    
    @property
    def wholepage_heading(self):
        return heading(buyCaps(self.name), self.level)

    @property
    def wholepage(self):
        return f'{self.wholepage_heading} {self.wholepage_contents}<p></p>'

    @property
    def category_title(self):
        titles = [self.title, self.matriarch.title]
        if self.level < 2:
            return self.title
        elif self.ancestor(2).name == 'Sample Texts':
            return '{0} - Sample Text in {1}'.format(*titles)
        else:
            return '{1} {0}'.format(*titles)

    def story_title(self, story_name):
        if not self.level:
            titles = [story_name]
        elif self.level == 1:
            titles = [self.title, story_name]
        else:
            titles = [self.title, self.matriarch.title, story_name]
        return ' &lt; '.join(titles)
        
    @property
    def main_contents(self):
        return f'<div class="main-contents">{html(self.text)}</div>'
    
    @property
    def wholepage_contents(self):
        return f'<div class="main-contents">{html(self.text, self.level)}</div>'

    def stylesheets(self, sheets):
        links = sheets.split(' ')
        links = [self.hyperlink(link, anchors=False) for link in links]
        template = '<link rel="stylesheet" type="text/css" href="{0}">\n'
        return ''.join([template.format(link) for link in links])

    def icon(self, icon):
        icon = self.hyperlink(icon, anchors=False)
        return f'<link rel="icon" type="image/png" href="{icon}">\n'

    @property
    def search_script(self):
        hyperlink = self.hyperlink('search.html', anchors=False)
        return ('    <script type="text/javascript">\n'
                'let href = window.location.href;\n'
                'if (href.indexOf("?") != -1 && href.indexOf("?highlight=") == -1) {\n'
                '    let term = href.replace(/(.*?\\?)(.*?)(#.*|$)/, "$2");\n'
                f'    window.location.href = `{hyperlink}?${{term}}&andOr=and`;\n'
                '}\n'
                '</script>\n')

    @property
    def toc(self):
        if self.is_root or self.is_leaf:
            return ''
        links = '\n'.join(
            [f'<p>{self.hyperlink(d)}</p>' for d in self.daughters])
        return ('<div class="toc">\n'
                f'{links}\n'
                '</div>')

    @property
    def links(self):
        return ('<label>\n'
                '  <input type="checkbox" class="menu">\n'
                '  <ul>\n  <li{0}>{2}</li>\n'
                '    <div class="javascript">\n'
                '      <form id="search">\n'
                '        <li class="search">\n'
                '          <input type="text" name="term">\n'
                '          <button type="submit">Search</button>\n'
                '        </li>\n'
                '      </form>\n'
                '    </div>\n'
                '   <div class="links{1}">'
                '  {{0}}'
                '   </div>'
                '</ul></label>').format(
                    ' class="normal"' if self.is_root else '',
                    '-root' if self.is_root else '',
                    self.hyperlink(self.root))

    @property
    def elder_links(self):
        return self.links.format(self.matriarch_links)

    @property
    def family_links(self):
        link_array = ''
        level = 0
        for relative in self.family:
            old_level = level
            level = relative.level
            if level > old_level:
                link_array += f'<ul class="level-{str(level)}">'
            elif level < old_level:
                link_array += (old_level - level) * '</ul>\n'
            if relative == self:
                link_array += f'<li class="normal">{self.name}</li>\n'
            else:
                link_array += f'<li>{self.hyperlink(relative)}</li>\n'
        link_array += (level) * '</ul>\n'
        return self.links.format(link_array)

    @property
    def matriarch_links(self):
        links = '\n'.join(map(self._link, self.matriarchs))
        return f'<ul>\n{links}\n</ul>'

    def _link(self, other):
        other = self.new(other.location)
        if self == other:
            return f'<li class="normal">{self.hyperlink(other)}</li>'
        else:
            return f'<li>{self.hyperlink(other)}</li>'

    @property
    def nav_footer(self):
        try:
            previous = self.hyperlink(self.predecessor, '&larr; Previous page')
        except IndexError:
            previous = ('<a href="http://www.tinellb.com">'
                        '&uarr; Go to Main Page</a>')
        try:
            next = self.hyperlink(self.successor, 'Next page &rarr;')
        except IndexError:
            if self.is_root:
                next = ''
            else:
                next = self.hyperlink(self.root, 'Return to Menu &uarr;')
        links = '\n'.join([f'<div>\n{x}\n</div>\n' for x in (previous, next)])
        return f'<div class="nav-footer">{links}</div>'

    def copyright(self, template):
        datestring = dt.strftime
        date = self.date
        if 4 <= date.day <= 20 or 24 <= date.day <= 30:
            suffix = 'th'
        else:
            suffix = ('th', 'st', 'nd', 'rd')[date.day % 10]
        template = template.replace('%t', suffix)
        return datestring(date, template)

    @property
    def scripts(self):
        if self.script:
            return f'<script>\n{self.script}\n</script>'
        else:
            return ''

    def html(self, template=None):
        page = template or default.template
        for (section, function) in [
            ('{search-script}', 'search_script'),
            ('{title-heading}', 'title_heading'),
            ('{main-contents}', 'main_contents'),
            ('{toc}', 'toc'),
            ('{nav-footer}', 'nav_footer'),
            ('{title}', 'title'),
            ('{scripts}', 'scripts')
        ]:
            if page.count(section):
                try:
                    page = page.replace(section, getattr(self, function))
                except TypeError:
                    raise TypeError(section, function)
        try:
            page = re.sub(r'{(.*?): (.*?)}', self.section_replace, page)
        except TypeError:
            raise TypeError(section, function)
        return page

    def section_replace(self, regex):
        main, sub = [regex.group(i+1) for i in range(2)]
        try:
            func, arg = sub.split(': ', 1)
            return getattr(self, f'{func}_{main}')(arg)
        except (AttributeError, TypeError, ValueError):
            try:
                return getattr(self, f'{sub}_{main}')
            except (AttributeError, TypeError):
                return getattr(self, main)(sub)

    def delete_html(self):
        with ignored(WindowsError):
            if self.has_children:
                shutil.rmtree(os.path.dirname(self.link))
            else:
                os.remove(self.link)

    def delete(self):
        self.delete_html()
        super().delete()
