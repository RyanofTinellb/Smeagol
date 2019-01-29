import os
import shutil
from node import Node
from datetime import datetime
from page_utils import *
from smeagol.translation import *
from smeagol.utils import *
from smeagol.defaults import default

markdown = Markdown()

class Page(Node):
    def __init__(self, tree, location):
        super(Page, self).__init__(tree, location)

    def __getattr__(self, attr):
        if attr in {'name', 'script', 'old'}:
            return self.find().get(attr, '')
        elif attr  in {'text'}:
            return self.find().get(attr, [])
        elif attr in {'position'}:
            return self.find().get(attr, '1.0')
        elif attr is 'date':
            try:
                date = self.find()['date']
                return datetime.strptime(date, '%Y-%m-%d')
            except (ValueError, KeyError):
                return datetime.now()
        elif attr in ('flatname', 'score'):
            try:
                key = 'name' if attr == 'flatname' else 'score'
                return self.find()['flatname'][key]
            except KeyError:
                self.refresh_flatname()
                return getattr(self, attr)
        else:
            return super(Page, self).__getattr__(attr)

    def __setattr__(self, attr, value):
        if attr == 'text':
            with ignored(AttributeError):
                value = filter(None, value.split('['))
            self.find()['text'] = value
        elif attr in {'name', 'position', 'old'}:
            self.find()[attr] = value
        else:
            super(Page, self).__setattr__(attr, value)

    def __str__(self):
        return '['.join(self.text)

    def update_date(self):
        self.find()['date'] = datetime.strftime(datetime.today(), '%Y-%m-%d')

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
        hyperlink = '{0}/{1}'.format(link, url) if link else url
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
        name = [self.url]
        score = 0
        change_text(double_letter, r'#\1', name)
        for points, pattern in enumerate(punctuation):
            score += score_pattern(name[0], pattern, radix, points + 1)
            remove_text('\\' + pattern, name)
        return dict(name=name[0], score=score)

    def __getitem__(self, entry):
        if entry is '':
            return self
        count = 0
        try:
            page = self.eldest_daughter
        except AttributeError:
            raise KeyError('{0} has no children'.format(self.name))
        try:
            while page.name != entry != count:
                page.next()
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
        return self <> other and self >= other

    def __le__(self, other):
        return self == other or self < other

    def sort(self):
        self.children = [child.find() for child in sorted(self.daughters)]

    def publish(self, template=None):
        text = self.html(template)
        if self.old <> text:
            dumps(text, self.link)
            self.old = text

    @property
    def list(self):
        if self.is_root:
            return []
        name = lambda x: x.name
        return map(name, self.lineage)[1:]

    @property
    def folder(self):
        return '/'.join(self.iterfolder)

    @property
    def iterfolder(self):
        for ancestor in self.ancestors:
            yield ancestor.url
        if not self.is_root and not self.is_leaf:
            yield self.url
        raise StopIteration

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
        link = '<a href="{0}">{1}</a>'.format(address, destination)
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
        link = '<a href="{0}">{1}</a>'.format(address, destination)
        return address, link

    @property
    def title(self):
        return remove_text(r'[[<].*?[]>]', [buyCaps(self.name)])[0]

    @property
    def title_heading(self):
        title = '<h1>{0}</h1>'
        return title.format(buyCaps(self.name))

    @property
    def category_title(self):
        if self.level < 2:
            return self.title
        else:
            if self.matriarch.name == 'Introduction':
                return self.title
            elif self.ancestor(2).name == 'Sample Texts':
                titles = [self.title, self.ancestor(1).title]
                return '{0} - Sample Text in {1}'.format(*titles)
            else:
                return self.matriarch.title + ' ' + self.title

    @property
    def story_title(self):
        if self.level == 0:
            return ''
        elif self.level == 1:
            return self.title
        else:
            return self.title + ' &lt; ' + self.matriarch.title

    @property
    def main_contents(self):
        contents = '<div class="main-contents">{0}</div>'
        return contents.format(html(self.text))

    def stylesheets(self, sheets):
        links = sheets.split(' ')
        links = [self.hyperlink(link, anchors=False) for link in links]
        template = '<link rel="stylesheet" type="text/css" href="{0}">\n'
        return ''.join([template.format(link) for link in links])

    def icon(self, icon):
        icon = self.hyperlink(icon, anchors=False)
        template = '<link rel="icon" type="image/png" href="{0}">\n'
        return template.format(icon)

    @property
    def search_script(self):
        hyperlink = self.hyperlink('search.html', anchors=False)
        return ('    <script type="text/javascript">\n'
                'let href = window.location.href;\n'
                'if (href.indexOf("?") != -1) {{\n'
                '    let term = href.replace(/(.*?\?)(.*?)(#.*|$)/, "$2");\n'
                '    window.location.href = `{0}?${{term}}&andOr=and`;\n'
                '}}\n'
            '</script>\n').format(hyperlink)

    @property
    def toc(self):
        if self.is_root or self.is_leaf:
            return ''
        toc = '<div class="toc">\n{0}\n</div>'
        hyperlinks = ['<p>{0}</p>'.format(self.hyperlink(daughter))
                            for daughter in self.daughters]
        return toc.format('\n'.join(hyperlinks))

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
                link_array += '<ul class="level-{0}">'.format(str(level))
            elif level < old_level:
                link_array += (old_level - level) * '</ul>\n'
            if relative == self:
                link_array += '<li class="normal">{0}</li>\n'.format(
                    self.name)
            else:
                link_array += '<li>{0}</li>\n'.format(
                    self.hyperlink(relative))
        link_array += (level - 1) * '</ul>\n'
        return self.links.format(link_array)

    @property
    def matriarch_links(self):
        links = '\n'.join(map(self._link, self.matriarchs))
        return '<ul>\n{0}\n</ul>'.format(links)

    def _link(self, other):
        other = self.new(other.location)
        if self == other:
            template = '<li class="normal">{0}</li>'
        else:
            template = '<li>{0}</li>'
        return template.format(self.hyperlink(other))

    @property
    def nav_footer(self):
        footer = '<div class="nav-footer">{0}</div>'
        div = '<div>\n{0}\n</div>\n'
        try:
            previous = self.hyperlink(self.predecessor,
                                      '&larr; Previous page')
        except IndexError:
            previous = ('<a href="http://www.tinellb.com">'
                        '&uarr; Go to Main Page</a>')
        try:
            next = self.hyperlink(self.successor, 'Next page &rarr;')
        except IndexError:
            if self == self.root:
                next = ''
            else:
                next = self.hyperlink(self.root, 'Return to Menu &uarr;')
        links = '\n'.join([div.format(f) for f in (previous, next)])
        return footer.format(links)

    def copyright(self, template):
        strftime = datetime.strftime
        date = self.date
        if 4 <= date.day <= 20 or 24 <= date.day <= 30:
            suffix = 'th'
        else:
            suffix = ('th', 'st', 'nd', 'rd')[date.day % 10]
        template = template.replace('%t', suffix)
        return strftime(date, template)

    def section_replace(self, regex):
        regex = [regex.group(i+1) for i in xrange(2)]
        if regex[0] in {'copyright', 'stylesheets', 'icon'}:
            return getattr(self, regex[0])(regex[1])
        else:
            return getattr(self, '{1}_{0}'.format(*regex))

    @property
    def scripts(self):
        if self.script:
            return '<script>\n{0}\n</script>'.format(self.script)
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

    def delete_html(self):
        with ignored(WindowsError):
            if self.has_children:
                shutil.rmtree(os.path.dirname(self.link))
            else:
                os.remove(self.link)

    def delete(self):
        self.delete_html()
        super(Page, self).delete()
