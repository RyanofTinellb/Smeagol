from smeagol import utils
import re

class Markup:
    def html(self, text):
        with utils.ignored(AttributeError):
            text = text.split('\n')
        self.table = False
        return '\n'.join([self.convert(line) for line in text])
    
    def convert(self, line):
        beginning_is = line.startswith
        if beginning_is('<table'):
            self.table = True
            return line
        elif beginning_is('</table>'):
            self.table = False
            return line
        elif beginning_is('<ul') or beginning_is('<ol'):
            self.list = True
            return line
        elif beginning_is('</ul>') or beginning_is('</ol>'):
            self.list = False
            return line
        elif self.table:
            return self._table(line)
        elif self.list:
            return f'<li>{line}</li>'
        elif re.match(r'</*(?:h|div)', line):
            return line
        else:
            return f'<p>{line}</p>'

    def _table(self, line):
        line = ' '.join([self._cell(cell) for cell in line.split('|')])
        line = f'<tr>{line}</tr>'
        return line
    
    def _cell(self, cell):
        if cell:
            try:
                form, cell = cell.rstrip().split(' ', 1)
            except ValueError:
                form, cell = cell, ''
        else:
            form, cell = '', cell
        heading = 'h' if 'h' in form else 'd'
        rowcol = list(map(self._rowcol, [
            ['rowspan', r'(?<=r)\d*', form],
            ['colspan', r'(?<=c)\d*', form]
        ]))
        return '<t{0}{2}{3}>{1}</t{0}>'.format(heading, cell, *rowcol)

    def _rowcol(self, info):
        try:
            return ' {0}="{1}"'.format(info.pop(0), re.search(*info).group(0))
        except AttributeError:
            return ''