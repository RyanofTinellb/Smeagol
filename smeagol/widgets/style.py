import re
import json

'''
properties:
    name => name
    key => key
    tags => tags
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
    border (str) => pargraph.relief
    justification (str) => paragraph.justify
    left, right, indent (int[]) => paragraph.{lmargin1, lmargin2, rmargin}
    top, bottom, line_spacing (int[]) => paragraph.{spacing1, spacing2, spacing3}

default:

'''

defaults = dict(name='default', key=None, tags=('', ''), group='default', size=18, font='Calibri',
                bold=False, italics=False, underline=False, strikeout=False, offset='baseline',
                colour='black', background='white', border=True, justification='left',
                unit='cm', left=0, right=0, top=0, bottom=0, indent=0, line_spacing=0)


class Style:
    def __init__(self, **style):
        if style.get('group', None) == 'default':
            for attr, value in style.items():
                try:
                    defaults[attr] = value
                except KeyError:
                    raise TypeError(
                        f'{type(self).__name__} object must have attribute "{attr}"')
        else:
            self.validate(style)
            for attr, value in style.items():
                setattr(self, attr, value)

    def validate(self, style):
        for attr in ['name', 'tags']:
            if style.get(attr, None) is None:
                raise TypeError(
                    f'{type(self).__name__} object must have attribute "{attr}"')

    def __getattr__(self, attr):
        if attr in {'_font', 'paragraph'}:
            super().__setattr__(attr, {})
            return getattr(self, attr)
        else:
            return defaults[attr]

    def __setattr__(self, attr, value):
        if attr == 'font':
            self._font['family'] = value
        elif attr == 'size':
            self._font['size'] = self._size(value)
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
        elif attr == 'justification':
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
            para = '' if end.endswith('\n') else '\n'
            super().__setattr__(attr, (start, f'{end}{para}'))
        elif attr == 'group':
            start, end = self.tags
            para = '' if end.endswith('\n') or value != 'paragraph' else '\n'
            self.tags = start, f'{end}{para}'
        elif attr == 'unit':
            self._change_units(value)
        elif attr not in {'name', 'tags', '_font', 'paragraph'}:
            raise AttributeError(
                f'{type(self).__name__} object has no attribute "{attr}"')

    def add_unit(self, value):
        return f'{value}{self.unit[0]}'

    def _change_units(self, value):
        unit = value[0]
        if unit in 'cpim':
            attrs = 'left', 'right', 'top', 'bottom', 'line_spacing', 'indent'
            for attr in attrs:
                value = getattr(self, attr)
                setattr(self, attr, value)
        else:
            raise AttributeError(
                f'unit "{value}" is not a valid unit for {type(self).__name__} object')

    def _size(self, value):
        if isinstance(value, str):
            default = self.style.size
            return max(int(value) + default, 0)
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