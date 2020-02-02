import re
import json
from contextlib import contextmanager
from tkinter.font import Font

'''
properties:
    name (str) => name
    key (str) => key
    tags (str()) => tags
    size (int): absolute size => font.size
         (str): relative size (include +/- sign)
    font (str) => font.family
    bold (bool) => font.weight
    italics (bool) => font.slant
    underline (bool) => font.underline
    strikeout (bool) => font.overstrike
    offset (str): superscript / subscript / baseline => paragraph.offset
    colour (str) => paragraph.foreground
    background (str) => paragraph.background
    border (str) => paragraph.relief
    justification (str) => paragraph.justify
    left, right, indent (int) => paragraph.{lmargin1, lmargin2, rmargin}
    top, bottom, line_spacing (int) => paragraph.{spacing1, spacing2, spacing3}
'''

defaults = dict(name='default', key='', tags=['', ''], group='font', font='Calibri', size=12,
                bold=False, italics=False, underline=False, strikethrough=False,
                offset='baseline', colour='black', background='white', border=False,
                justification='left', unit='cm', indent=0.0, line_spacing=0.0,
                left=0.0, right=0.0, top=0.0, bottom=0.0, language=False, hyperlink=False)

attrs = ('group', 'key', 'font', 'size', 'bold', 'italics', 'underline', 'strikethrough', 'offset',
         'colour', 'background', 'border', 'justification', 'unit', 'left', 'right',
         'top', 'bottom', 'indent', 'line_spacing', 'language', 'hyperlink')


@contextmanager
def ignored(*exceptions):
    try:
        yield
    except exceptions:
        pass


def _int_part(_dict, key):
    value = _dict.get(key, 0)
    try:
        return int(value)
    except ValueError:
        try:
            return int(re.sub(r'\D', '', value))
        except ValueError:
            return 0


class Style:
    def __init__(self, **style):
        if style.get('group', None) == 'default':
            for attr, value in style.items():
                if attr == 'size':
                    value = self._size(value)
                setattr(self, attr, value)
                defaults[attr] = value
        else:
            for attr, value in style.items():
                setattr(self, attr, value)

    def __getattr__(self, attr):
        if attr in {'_font', 'paragraph'}:
            super().__setattr__(attr, {})
            return getattr(self, attr)
        elif attr == 'rounding':
            return int if self.unit[0] in 'mp' else float
        elif attr == 'group':
            return 'font'
        elif attr == 'defaults':
            return defaults
        elif attr == 'Font':
            return Font(**self._font)
        else:
            return defaults[attr]

    def __setattr__(self, attr, value):
        if attr in ('left', 'right', 'top', 'bottom', 'line_spacing', 'indent'):
            value = self.rounding(value)
        super().__setattr__(attr, value)
        if attr == 'font':
            self._font['family'] = value
        elif attr == 'size':
            size = self._size(value)
            self._font['size'] = size
            super().__setattr__('size', size)
        elif attr == 'bold':
            self._font['weight'] = 'bold' if value else 'normal'
        elif attr == 'italics':
            self._font['slant'] = 'italic' if value else 'roman'
        elif attr == 'underline':
            self._font['underline'] = value
        elif attr == 'strikethrough':
            self._font['overstrike'] = value
        elif attr == 'background':
            self.paragraph['background'] = value
        elif attr == 'colour':
            self.paragraph['foreground'] = value
        elif attr == 'border':
            self.paragraph['relief'] = 'ridge' if value else 'flat'
            self.paragraph['borderwidth'] = 2 if value else 0
        elif attr == 'justification':
            value = 'center' if value == 'centre' else value
            self.paragraph['justify'] = value
        elif attr == 'offset':
            self._font['size'], self.paragraph['offset'] = self._offset(value)
        elif attr == 'top':
            self.paragraph['spacing1'] = self.add_unit(value)
        elif attr == 'bottom':
            self.paragraph['spacing3'] = self.add_unit(value)
        elif attr == 'left':
            self.paragraph['lmargin1'], self.paragraph['lmargin2'] = self._left(
                value)
        elif attr == 'right':
            self.paragraph['rmargin'] = self.add_unit(value)
        elif attr == 'indent':
            self.paragraph['lmargin1'] = self.add_unit(self.left + value)
        elif attr == 'line_spacing':
            self.paragraph['spacing2'] = self.add_unit(value)
        elif attr == 'tags':
            start, end = value
            para = '' if end.endswith(
                '\n') or self.group != 'paragraph' else '\n'
            super().__setattr__(attr, (start, f'{end}{para}'))
        elif attr == 'group':
            start, end = self.tags
            para = '' if end.endswith('\n') or value != 'paragraph' else '\n'
            self.tags = start, f'{end}{para}'
        elif attr == 'unit':
            self._change_units(value)

    def add_unit(self, value):
        return f'{value}{self.unit[0]}'

    def _change_units(self, value):
        unit = value[0]
        if unit in 'cpim':
            rounding = float if unit in 'ci' else int
            attrs = 'left', 'right', 'top', 'bottom', 'line_spacing', 'indent'
            for attr in attrs:
                value = getattr(self, attr)
                setattr(self, attr, rounding(value))
        else:
            raise AttributeError(
                f'unit "{value}" is not a valid unit for {type(self).__name__} object')

    def _size(self, value):
        if isinstance(value, str):
            return max(int(value) + defaults['size'], 1)
        else:
            return value

    def _offset(self, value):
        basesize = self.size
        if value == 'baseline':
            return basesize, 0
        size = basesize * 2 // 3
        if value == 'superscript':
            offset = basesize - size
        elif value == 'subscript':
            offset = (size - basesize) // 2
        return size, offset

    def _left(self, value):
        left1 = self.add_unit(value + self.indent)
        left2 = self.add_unit(value)
        return left1, left2

    def copy(self):
        return Style(**self.style.copy())

    def items(self, attrs=attrs):
        for attr in attrs:
            yield attr, getattr(self, attr)

    def unique_items(self, attrs=attrs, defaults=defaults):
        for attr in ('name', 'tags') + attrs:
            value = getattr(self, attr)
            if value != defaults[attr] or attr == 'group' or self.group == 'default':
                yield attr, value

    @property
    def style(self, defaults=defaults):
        return dict(self.unique_items(defaults=defaults))