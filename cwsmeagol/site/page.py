import os
import node
from cwsmeagol.translation import *
from cwsmeagol.utils import *
from cwsmeagol.defaults import default


def analyse(text, markdown=None):
    markdown = markdown or Markdown()
    wordlist = {}
    content = [text]
    # remove tags, and items between some tags
    change_text(r'\[\d\]|<(ipa|high-lulani|span).*?</\1>|<.*?>', ' ', content)
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
    content = [markdown.to_markdown(content).lower()]
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


alphabet = " aeiyuow'pbtdcjkgmnqlrfvszxh"
punctuation = "$-'#.()!_"
radix = len(punctuation)
double_letter = r'([{0}])\1'.format(alphabet)


def flatname(name):
    if name is None:
        name = ''
    name = [urlform(name)]
    score = 0
    change_text(double_letter, r'\1#', name)
    for points, pattern in enumerate(punctuation):
        score += score_pattern(name[0], pattern, radix, points + 1)
        remove_text('\\' + pattern, name)
    return dict(name=name[0], score=score)


def score_pattern(word, pattern, radix, points):
    return sum([points * radix**index
                for index in pattern_indices(word, pattern)])


def pattern_indices(word, pattern):
    index = -1
    while True:
        try:
            index = word.index(pattern, index + 1)
            yield index + 1
        except ValueError:
            raise StopIteration


def compare_flatnames(one, other):
    if one.name == other.name:
        if one.score == other.score:
            return 0
        else:
            return 1 if one.score > other.score else -1
    for s, t in zip(one.name, other.name):
        if s != t:
            try:
                return 1 if alphabet.index(s) < alphabet.index(t) else -1
            except ValueError:
                continue
    else:
        return 1 if len(one.name) < len(other.name) else -1


def folder(root, location):
    return '/'.join(iterfolder(root, location))


def iterfolder(root, location):
    ancestors = node.ancestors(root, location)
    ancestors.next()
    for ancestor in ancestors:
        yield urlform(node.name(root, ancestor))
    if len(location) and not node.is_leaf(root, location):
        yield urlform(node.name(root, location))
    raise StopIteration


def link(root, location, extend=True):
    link = folder(root, location)
    entry = node.find(root, location)
    url = '{0}{1}'.format(
        url(root, location) if len(entry['children']) == 0 else 'index',
        '.html' if extend else '')
    return '{0}/{1}'.format(link, url) if link else url


def hyperlink(root, source, destination, template='{0}', anchor_tags=True):
    if list(destination) == list(source):
        return template.format(node.name(root, destination))
    try:
        address, link = _direct(root, source, destination, template)
    except AttributeError:  # destination is a string
        address, link = _indirect(root, source, destination, template)
    return link if anchor_tags else address


def _indirect(root, source, destination, template):
    up = len(source) + int(node.has_children(root, source)) - 1
    address = (up * '../') + destination
    link = '<a href="{0}">{1}</a>'.format(address, template.format(destination))
    return address, link


def _direct(root, source, destination, template):
    change = int(not node.is_leaf(root, source))
    if not len(destination):
        up = len(source) + change - 1
        down = 'index'
        extension = '.html'
    else:
        if node.startswith(destination, source):
            up = len(source) + change - len(destination)
            down = node.url(root, destination)
        else:
            up = len(source) + change - node.cousin_degree(source, destination)
            down = '/'.join([node.url(root, ancestor) for ancestor in
                    node.unshared_ancestors(root, destination, source)])
        extension = '.html' if node.is_leaf(root, destination) else '/index.html'
    address = (up * '../') + down + extension
    link = '<a href="{0}">{1}</a>'.format(address,
                        template.format(buyCaps(node.name(root, destination))))
    return address, link


def change_to_heading(text):
    try:
        level, name = text.split(']')
    except ValueError:
        raise AttributeError(text)
    if level == '1':
        name = buyCaps(name)
    url_id = urlform(re.sub(r'\(.*?\)', '', name))
    if url_id:
        return '<h{0} id="{1}">{2}</h{0}>\n'.format(level, url_id, name)
    else:
        return '<h{0}>{1}</h{0}>\n'.format(level, name)


def change_to_div(text, divclass=None):
    divclass = divclass or []
    if text.startswith('/'):
        if divclass and divclass.pop() == 'folding':
            return '</div></label>'
        return '</div>'
    else:
        divclass.append(text[2:-1])
        if divclass[-1] == 'folding':
            return ('<label class="folder">'
                    '<input type="checkbox" class="folder">'
                    '<div class="folding">')
        elif divclass[-1] == 'interlinear':
            return '''<div class="interlinear">
    <input class="version" type="radio" name="version" id="All" checked>All
    <input class="version" type="radio" name="version" id="English">English
    <input class="version" type="radio" name="version" id="Tinellbian">Tinellbian
    <input class="version" type="radio" name="version" id="Transliteration">Transliteration'''
        return '<div class="{0}">'.format(divclass[-1])


def change_to_table(text):
    text = text[2:]
    rows = ''.join(map(table_row, text.splitlines()))
    return '<{0}>\n{1}</{0}>\n'.format('table', rows)


def table_row(row):
    cells = ''.join(map(table_cell, row.split('|')))
    return '<{0}>\n{1}\n</{0}>\n'.format('tr', cells)


def table_cell(cell):
    if cell.startswith(' ') or cell == '':
        form, cell = '', cell[1:]
    else:
        try:
            form, cell = cell.split(' ', 1)
        except ValueError:
            form, cell = cell, ''
    heading = 'h' if 'h' in form else 'd'
    rowcol = map(check_rowcol, [
        ['rowspan', r'(?<=r)\d*', form],
        ['colspan', r'(?<=c)\d*', form]
    ])
    return '<t{0}{2}{3}>\n{1}\n</t{0}>\n'.format(heading, cell, *rowcol)


def check_rowcol(info):
    try:
        return ' {0}="{1}"'.format(info.pop(0), re.search(*info).group(0))
    except AttributeError:
        return ''


def title(root, location):
    return remove(r'[[<].*?[]>]', [node.name(root, location)])[0]


def category_title(root, location):
    if len(location) < 2:
        return title(root, location)
    else:
        if node.name(root, location[:1]) == 'Introduction':
            return title(root, location)
        else:
            return title(root, location[:1]) + ' ' + title(root, location)


def contents(text):
    mode = [None]
    return [convert(line, mode) for line in text]

section_mark = {'n': '<ol>',
                '/n': '</ol>',
                'l': '<ul>',
                '/l': '</ul>',
                'e': '<p class="example_no_lines">',
                'f': '<p class="example">'}

delimiters = {'n': 'li', 'l': 'li'}

def convert(line, mode):
    delimiter = 'p'
    marks = True
    try:
        category, rest = line.split('\n', 1)
    except ValueError:
        category, rest = '', line
    if re.match(r'\d\]', line):
        category = change_to_heading(category)
    elif re.match(r'\/*d', line):
        category = change_to_div(category)
    elif line.startswith('t'):
        category = change_to_table(line)
    elif line.startswith('/t]'):
        category = ''
    else:
        try:
            category, remainder = category.split(']', 1)
            if category.startswith('/'):
                mode.pop()
            elif category in ('n', 'l'):
                mode.append(category)
            elif category in ('e', 'f'):
                marks = False
            delimiter = delimiters.get(mode[-1], 'p')
            category = section_mark.get(category, '<p>')
        except ValueError:
            category, remainder = '', category
        rest = remainder + '\n' + rest
    try:
        return category + '\n' + paragraphs(rest, delimiter, marks)
    except TypeError:
        raise TypeError(category)


def paragraphs(text, delimiter='p', marks=True):
    text = re.sub(r'^\n|\n$', '', text)
    if text == '\n' or text == '':
        return ''
    if marks:
        return '<{{0}}>{0}</{{0}}>'.format(
            '</{0}>\n<{0}>'.join(text.splitlines())).format(delimiter)
    return '{0}</{{0}}>'.format(
        '</{0}>\n<{0}>'.join(text.splitlines())).format(delimiter)


def stylesheet_and_icon(root, source):
    return ('<link rel="stylesheet" type="text/css" href="{0}">\n'
            '<link rel="stylesheet" type="text/css" href="{1}">\n'
            '<link rel="icon" type="image/png" href="{2}">\n').format(
                *[hyperlink(root, source, destination) for destination in [
                        'basic_style.css', 'style.css', 'favicon.png']])


def search_script(root, source):
    return ('<script type="text/javascript">'
                'if (window.location.href.indexOf("?") != -1) {{'
                'window.location.href = "{0}" +'
                'window.location.href.substring('
                'window.location.href.indexOf("?")) + "&andOr=and";'
                '}}'
                '</script>').format(hyperlink('search.html', anchor_tags=False))


def toc(root, location):
    children = node.num_children(root, location)
    if children and len(source):  # self not root nor leaf
        return ''.join(['<p>{0}</p>\n'.format(hyperlink(root, location, child))
            for child in xrange(children)])
    else:
        return ''


def links(root, location):
    return ('<label>\n'
            '  <input type="checkbox" class="menu">\n'
            '  <ul>\n  <li{0}>{1}</li>\n'
            '    <div class="javascript">\n'
            '      <form id="search">\n'
            '        <li class="search">\n'
            '          <input type="text" name="term"></input>\n'
            '          <button type="submit">Search</button>\n'
            '        </li>\n'
            '      </form>\n'
            '    </div>\n'
            '  {{0}}'
            '</ul></label>').format(
                ' class="normal"' if not len(location) else '',
                hyperlink(root, location, []))


def family_links(root, location):
    link_array = ''
    level = 1
    for page in node.family(root, location):
        old_level = level
        level = len(page)
        if level > old_level:
            link_array += '<ul class="level-{0}">'.format(str(level))
        elif level < old_level:
            link_array += (old_level - level) * '</ul>\n'
        if page == tuple(location):
            link_array += '<li class="normal">{0}</li>\n'.format(
                node.name(root, location))
        else:
            link_array += '<li>{0}</li>\n'.format(
                hyperlink(root, location, page))
    link_array += (level) * '</ul>\n'
    return links(root, location).format(link_array)


def elder_links(root, location):
    return links(root, location).format(matriarch_links(root, location))


def matriarch_links(root, location):
    return '<ul>\n{0}\n</ul>'.format('\n'.join([
                    '<li{0}>{1}</li>'.format(
                    ' class="normal"' if matriarch == (location[1],) else '',
                            hyperlink(root, location, matriarch))
                                    for matriarch in node.matriarchs(root, location)]))


def nav_footer(root, location):
    div = '<div>\n{0}\n</div>\n'
    try:

        output = div.format(hyperlink(root, location,
                node.previous(root, location[:]), '&larr; Previous page'))
    except IndexError:
        output = div.format(
            '<a href="http://www.tinellb.com">&uarr; Go to Main Page</a>')
    try:
        output += div.format(hyperlink(root, location,
                node.next(root, location[:]), 'Next page &rarr;'))
    except IndexError:
        output += div.format(hyperlink(root, location,
                    [], 'Return to Menu &uarr;'))
    return output


def date(root, location):
    try:
        return datetime.strptime(node.date(root, location), '%Y-%m-%d')
    except ValueError:
        return datetime.now()


def copyright(root, location):
    cdate = date(root, location)
    suffix = "th" if 4 <= cdate.day <= 20 or 24 <= cdate.day <= 30 else [
        "st", "nd", "rd"][cdate.day % 10 - 1]
    return datetime.strftime(
        cdate, ('<span class="no-breaks">&copy;%Y '
               '<a href="http://www.tinellb.com/about.html">'
               'Ryan Eakins</a>.</span> <span class="no-breaks">'
               'Last updated: %A, %B %#d' + suffix + ', %Y.'))


def publish(root, location=[], template=None):
    page = template or default.template
    for (section, function) in [
        ('{title}', 'title'),
        ('{stylesheet}', 'stylesheet_and_icon'),
        ('{search-script}', 'search_script'),
        ('{content}', 'contents'),
        ('{toc}', 'toc'),
        ('{family-links}', 'family_links'),
        ('{elder-links}', 'elder_links'),
        ('{nav-footer}', 'nav_footer'),
        ('{copyright}', 'copyright'),
        ('{category-title}', 'category_title')
    ]:
        if page.count(section):
            page = page.replace(section, getattr(self, function))


def delete_htmlfile(root, location):
    with ignored(WindowsError):
        os.remove_text(link(root, location))
