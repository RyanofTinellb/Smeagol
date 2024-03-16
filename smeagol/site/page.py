from datetime import datetime as dt
from smeagol.utilities import utils
from smeagol.site.entry import Entry


class Page(Entry):
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
        utils.remove_text(
            r'(?<=\n) +| +(?=[\n ])|^ +| +$|\n+(?=\n)|[,:]', content)
        # remove duplicate end-lines, and tags in square brackets
        utils.remove_text(r'\n+(?=\n)|\[.*?\]', content)
        content = utils.buyCaps(content[0])
        lines = content.splitlines()
        content = [content.lower()]
        utils.change_text(r'&.*?;', ' ', content)
        # change punctuation, and tags in square brackets, into spaces
        utils.change_text(
            r'\'\"|\[.*?\]|[!?`\"/{}\\;-]|\'($| )|\d', ' ', content)
        # make glottal stops lower case where appropriate
        utils.change_text(r"(?<=[ \n])''", "'", content)
        for number, line in enumerate(content[0].splitlines()):
            for word in line.split():
                try:
                    if wordlist[word][-1] != number:
                        wordlist[word].append(number)
                except KeyError:
                    wordlist[word] = [number]
        return {'words': wordlist, 'sentences': lines}

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
    # pylint: disable=C0209
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
            next_ = self.hyperlink(self.successor, 'Next page &rarr;')
        except IndexError:
            if self.is_root:
                next_ = ''
            else:
                next_ = self.hyperlink(self.root, 'Return to Menu &uarr;')
        links = '\n'.join([f'<div>\n{x}\n</div>\n' for x in (previous, next_)])
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
        return f'<script>\n{self.script}\n</script>' if self.script else ''
