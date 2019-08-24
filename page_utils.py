import re

from smeagol.utils import *

alphabet = " aeiyuow'pbtdcjkgmnqlrfvszxh"
punctuation = "$-.#()!_"
radix = len(punctuation)
double_letter = rf'([^{punctuation}])\1'


def score_pattern(word, pattern, radix, points):
    return sum([points * radix**index
                for index in pattern_indices(word, pattern)])


def pattern_indices(word, pattern):
    index = -1
    while True:
        try:
            index = word.index(pattern, index + 1)
            yield index
        except ValueError:
            return


def html(text=None):
    mode = [None]
    divs = [None]
    return '\n'.join([convert(line, mode, divs) for line in text])


section_mark = {'n': '<ol>',
                '/n': '</ol>',
                'l': '<ul>',
                '/l': '</ul>',
                'e': '<p class="example_no_lines">',
                'f': '<p class="example">',
                'e ': '<p class="example_no_lines">',
                'f ': '<p class="example">'}

delimiters = {'n': 'li', 'l': 'li'}


def convert(line, mode, divs):
    delimiter = 'p'
    marks = True
    try:
        category, rest = line.split('\n', 1)
    except ValueError:
        category, rest = line, ''
    if re.match(r'\d\]', line):
        category = heading(category)
    elif re.match(r'\/*d', line):
        category = div(category, divs)
    elif line.startswith('t'):
        category = table(line)
        rest = ''
    elif line.startswith('/t]'):
        category = ''
    else:
        try:
            category, remainder = category.split(']', 1)
            if category.startswith('/'):
                mode.pop()
            elif category in ('n', 'l'):
                mode.append(category)
            elif category in ('e', 'f', 'e ', 'f '):
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


def div(div_, divs):
    if div_.startswith('/'):
        if divs and divs.pop() == 'folding':
            return '</div></label>'
        return '</div>'
    else:
        div_ = div_[2:-1]
        divs.append(div_)
        if div_ == 'folding':
            return ('<label class="folder">'
                    '<input type="checkbox" class="folder">'
                    '<div class="folding">')
        elif div_ == 'interlinear':
            return ('<div class="interlinear">'
                    '<input class="version" type="radio" '
                    'name="version" id="All" checked>All'
                    '<input class="version" type="radio" '
                    'name="version" id="English">English'
                    '<input class="version" type="radio" '
                    'name="version" id="Tinellbian">Tinellbian'
                    '<input class="version" type="radio" '
                    'name="version" id="Transliteration">'
                    'Transliteration')
        return '<div class="{0}">'.format(div_)


def heading(text):
    try:
        level, name = text.split(']')
        level = int(level) + 1
    except ValueError:
        raise AttributeError(text)
    url_id = urlform(re.sub(r'\(.*?\)| ', '', name))
    if url_id:
        return '<h{0} id="{1}">{2}</h{0}>\n'.format(level, url_id, name)
    else:
        return '<h{0}>{1}</h{0}>\n'.format(level, name)


def table(text):
    text = text[2:]
    rows = ''.join(map(table_row, text.splitlines()))
    return '<{0}>\n{1}</{0}>\n'.format('table', rows)


def table_row(row):
    cells = ''.join(map(table_cell, row.split('|')))
    return '<{0}>{1}</{0}>\n'.format('tr', cells)


def table_cell(cell):
    if cell.startswith(' ') or cell == '':
        form, cell = '', cell[1:]
    else:
        try:
            form, cell = cell.split(' ', 1)
        except ValueError:
            form, cell = cell, ''
    heading = 'h' if 'h' in form else 'd'
    rowcol = list(map(check_rowcol, [
        ['rowspan', r'(?<=r)\d*', form],
        ['colspan', r'(?<=c)\d*', form]
    ]))
    return '<t{0}{2}{3}>{1}</t{0}>'.format(heading, cell, *rowcol)


def check_rowcol(info):
    try:
        return ' {0}="{1}"'.format(info.pop(0), re.search(*info).group(0))
    except AttributeError:
        return ''
