import os
from node import Node
from datetime import datetime
from page_utils import *
from cwsmeagol.translation import *
from cwsmeagol.utils import *
from cwsmeagol.defaults import default


class Page(Node):
    def __init__(self, tree, location):
        super(Page, self).__init__(tree, location)

    def __getattr__(self, attr):
        if attr in ('name', 'text'):
            return self.find().get(attr, '')
        elif attr is 'date':
            try:
                date = self.find()['date']
                return datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                return datetime.now()
        elif attr in ('flatname', 'score'):
            try:
                key = 'name' if attr == 'flatname' else 'score'
                return self.find()['flatname'][key]
            except KeyError:
                self.refresh_flatname()
                return getattr(self, attr)
        elif attr is 'link':
            try:
                return self.find()['hyperlink']
            except KeyError:
                self.refresh_hyperlink()
                return getattr(self, attr)
        else:
            return super(Page, self).__getattr__(attr)

    def __setattr__(self, attr, value):
        if attr == 'text':
            self.find()['text'] = value
        else:
            super(Page, self).__setattr__(attr, value)


    def __str__(self):
        return '['.join(self.text)

    def update_date(self):
        self.find()['date'] = datetime.strftime(datetime.today(), '%Y-%m-%d')

    def refresh_flatname(self):
        self.find()['flatname'] = self._flatname

    def remove_flatname(self):
        with ignored(KeyError):
            self.find().pop('flatname')

    def refresh_hyperlink(self):
        link = self.folder
        url = self.url if not self.has_children else 'index'
        hyperlink = '{0}/{1}'.format(link, url) if link else url
        self.find()['hyperlink'] = hyperlink

    @property
    def level(self):
        return len(self.location)

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
            r'\[\d\]|<(ipa|high-lulani|span).*?</\1>|<.*?>', ' ', content)
        # remove datestamps
        remove_text(r'&date=\d{8}', content)
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
        content = [Markdown().to_markdown(content).lower()]
        # change punctuation, and tags in square brackets, into spaces
        change_text(r'\'\"|\[.*?\]|[!?`\"/{}\\;-]|\'($| )|&nbsp', ' ', content)
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
            return self.flatname == other.flatname and self.score == other.score
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

    def publish(self, template=None):
        dumps(self.html(template), self.link)

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
        down = '/'.join([ancestor.url for ancestor in
                            destination.unique_lineage(self)])
        address = (up * '../') + down + '.html'
        destination = template.format(buyCaps(destination.name))
        link = '<a href="{0}">{1}</a>'.format(address, destination)
        return address, link

    @property
    def title(self):
        return remove_text(r'[[<].*?[]>]', [self.name])[0]

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
            else:
                return self.matriarch.title + ' ' + self.title

    @property
    def main_contents(self):
        contents = '<div class="main-contents">{0}</div>'
        return contents.format(html(self.text))

    @property
    def stylesheet_and_icon(self):
        destinations = ['basic_style.css', 'style.css', 'favicon.png']
        hyperlinks = [self.hyperlink(destination, anchors=False)
                        for destination in destinations]
        return ('<link rel="stylesheet" type="text/css" href="{0}">\n'
                '<link rel="stylesheet" type="text/css" href="{1}">\n'
                '<link rel="icon" type="image/png" href="{2}">\n'
                ).format(*hyperlinks)

    @property
    def search_script(self):
        hyperlink = self.hyperlink('search.html', anchors=False)
        return ('<script type="text/javascript">'
                'if (window.location.href.indexOf("?") != -1) {{'
                'window.location.href = "{0}" +'
                'window.location.href.substring('
                'window.location.href.indexOf("?")) + "&andOr=and";'
                '}}'
                '</script>').format(hyperlink)

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
                '  <ul>\n  <li{0}>{1}</li>\n'
                '    <div class="javascript">\n'
                '      <form id="search">\n'
                '        <li class="search">\n'
                '          <input type="text" name="term">\n'
                '          <button type="submit">Search</button>\n'
                '        </li>\n'
                '      </form>\n'
                '    </div>\n'
                '   <div class="links">'
                '  {{0}}'
                '   </div>'
                '</ul></label>').format(
                    ' class="normal"' if not self.is_root else '',
                    self.hyperlink(self.root))

    @property
    def elder_links(self):
        return self.links.format(self.matriarch_links)

    @property
    def family_links(self):
        link_array = ''
        level = 1
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
            next = 'Return to Menu &uarr;'
        links = '\n'.join([div.format(f) for f in (previous, next)])
        return footer.format(links)

    @property
    def copyright(self):
        strftime = datetime.strftime
        copyright = '<div class="copyright">{0}</div>'
        date = self.date
        if 4 <= date.day <= 20 or 24 <= date.day <= 30:
            suffix = 'th'
        else:
            suffix = ['st', 'nd', 'rd'][date.day % 10 - 1]
        span = '<span class="no-breaks">{0}</span>'
        templates = (('&copy;%Y '
                      '<a href="http://www.tinellb.com/about.html">'
                      'Ryan Eakins</a>.'),
                'Last updated: %A, %B %#d' + suffix + ', %Y.')
        spans = '\n'.join([span.format(strftime(date, template))
                            for template in templates])
        return copyright.format(spans)

    def html(self, template=None):
        page = template or default.template
        for (section, function) in [
            ('{title}', 'title'),
            ('{stylesheet}', 'stylesheet_and_icon'),
            ('{search-script}', 'search_script'),
            ('{title-heading}', 'title_heading'),
            ('{main-contents}', 'main_contents'),
            ('{toc}', 'toc'),
            ('{family-links}', 'family_links'),
            ('{elder-links}', 'elder_links'),
            ('{nav-footer}', 'nav_footer'),
            ('{copyright}', 'copyright'),
            ('{category-title}', 'category_title')
        ]:
            if page.count(section):
                try:
                    page = page.replace(section, getattr(self, function))
                except TypeError:
                    raise TypeError(section, function)
        return page

    def delete_htmlfile(self):
        with ignored(WindowsError):
            os.remove_text(self.link + '.html')
