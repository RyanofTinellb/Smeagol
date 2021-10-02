import re
from datetime import datetime as dt

from ..utilities import utils
from .node import Node


class Entry(Node):
    def __init__(self, tree=None, location=None):
        super().__init__(tree, location)

    def __str__(self):
        return '\n'.join(self.text)

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
            with utils.ignored(AttributeError):
                value = [_f for _f in value.splitlines() if _f]
            self.find()['text'] = value
        elif attr in {'name', 'position', 'script', 'id'}:
            if value:
                self.find()[attr] = value
            else:
                self.find().pop(attr, None)
        else:
            super().__setattr__(attr, value)

    def update_date(self):
        self.find()['date'] = dt.strftime(dt.today(), '%Y-%m-%d')

    def remove_script(self):
        self.find().pop('script', None)
    
    def replace(self, old, new):
        self.text = '\n'.join(self.text).replace(old, new)
    
    def regex_replace(self, pattern, repl):
        self.text = re.sub(pattern, repl, '\n'.join(self.text))

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
        return utils.urlform(self.name)
    
    @property
    def analysis(self):
        wordlist = {}
        content = [str(self)]
        # remove tags, and items between some tags
        utils.change_text(
            r'\[\d\]|<(ipa|high-lulani|span).*?</\1>|<.*?>|^\d\]', ' ', content)
        # remove heading markers from tables
        utils.remove_text(r'\|\w*', content)
        # change punctuation to paragraph marks, so that splitlines works
        utils.change_text(r'[!?.|]', '\n', content)
        # change punctuation to space
        utils.change_text(r'[_()]', ' ', content)
        # remove spaces at the beginnings and end of lines,
        #    duplicate spaces and end-lines
        utils.remove_text(r'(?<=\n) +| +(?=[\n ])|^ +| +$|\n+(?=\n)|[,:]', content)
        # remove duplicate end-lines, and tags in square brackets
        utils.remove_text(r'\n+(?=\n)|\[.*?\]', content)
        content = utils.buyCaps(content[0])
        lines = content.splitlines()
        content = [content.lower()]
        utils.change_text(r'&.*?;', ' ', content)
        # change punctuation, and tags in square brackets, into spaces
        utils.change_text(r'\'\"|\[.*?\]|[!?`\"/{}\\;-]|\'($| )|\d', ' ', content)
        # make glottal stops lower case where appropriate
        utils.change_text(r"(?<=[ \n])''", "'", content)
        for number, line in enumerate(content[0].splitlines()):
            for word in line.split():
                try:
                    if wordlist[word][-1] != number:
                        wordlist[word].append(number)
                except KeyError:
                    wordlist[word] = [number]
        return dict(words=wordlist,
                    sentences=lines)

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
        destination = template.format(utils.buyCaps(destination.name))
        link = f'<a href="{address}">{destination}</a>'
        return address, link

    @property
    def title(self):
        return utils.remove_text(r'[\[<].*?[\]>]', [utils.buyCaps(self.name)])[0]
    
    def heading(self, name, level=1):
        return f'<h{level}>{name}</h{level}>'

    @property
    def title_heading(self):
        return self.heading(utils.buyCaps(self.name))
    
    @property
    def wholepage_heading(self):
        return self.heading(utils.buyCaps(self.name), self.level)

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
        text = '\n'.join(self.text)
        return f'<div class="main-contents">{text}</div>'
    
    @property
    def wholepage_contents(self):
        return f'<div class="main-contents">{self.text}</div>'

    def stylesheets(self, sheets):
        links = sheets.split(' ')
        links = [self.hyperlink(link, anchors=False) for link in links]
        template = '<link rel="stylesheet" type="text/css" href="{0}">'
        return '\n'.join([template.format(link) for link in links])

    def icon(self, icon):
        icon = self.hyperlink(icon, anchors=False)
        return f'<link rel="icon" type="image/png" href="{icon}">'

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
                '  <ul>\n'
                '    <li{0}>{2}</li>\n'
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