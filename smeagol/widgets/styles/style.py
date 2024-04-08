"""
properties:
    font (str) => font.family
    size (int|str) => font.size
    bold (bool) => font.weight
    italics (bool) => font.slant
    underline (bool) => font.underline
    strikeout (bool) => font.overstrike
    offset (str): superscript / subscript / baseline => paragraph.offset
    colour (str) => paragraph.foreground
    background (str) => paragraph.background
    border (bool) => paragraph.relief, paragraph.borderwidth
    justification (str) => paragraph.justify
    unit (str): centimetres, inches, pixels, points, millimetres
    left, right, indent (Number) => paragraph.{lmargin1, lmargin2, rmargin}
    top, bottom, line_spacing (Number) => paragraph.{spacing1, spacing2, spacing3}
"""

from tkinter.font import Font
from typing import Self

from smeagol.utilities import utils
from smeagol.widgets.styles.tag import Tag
from smeagol.utilities.defaults import default


class Style(Tag):
    def __init__(self, tags: dict = None, props: dict = None, default_style: Self = None):
        super().__init__(tags)
        self.props = props or {}
        self.default_style = default_style or {}
        if self._is_default:
            self._unchanged = self.props.copy()

    @property
    def style(self):
        return {'props': self.props, 'tags': self.tags}

    def __getitem__(self, attr):
        try:
            return self.props.get(attr)
        except KeyError as e:
            raise KeyError(
                f"'{type(self).__name__}' object has no item '{attr}'") from e

    def __setitem__(self, attr, value):
        self.props.setdefault(attr, value)

    def get(self, attr, default_value):
        match attr:
            case 'props' | 'tags':
                return self.style[attr]
            case _else:
                try:
                    return self.props[attr]
                except KeyError:
                    return default_value

    @property
    def has_font(self):
        for attr in ('font', 'size', 'bold', 'italics', 'underline', 'strikeout'):
            with utils.ignored(KeyError):
                return self.props[attr]
        return None

    @property
    def font(self):
        return utils.filter_nonzero({
            'family': self._family,
            'size': self._size,
            'weight': self._bold,
            'slant': self._italics,
            'underline': self['underline'],
            'overstrike': self['strikeout'],
        })

    @property
    def _bold(self):
        return 'bold' if self['bold'] else None

    @property
    def _italics(self):
        return 'italic' if self['italics'] else None

    @property
    def paragraph(self):
        return utils.filter_nonzero({
            'justify': self._justify,
            'offset': self._offset,
            **self.textbox_settings,
            **self._border,
            **self._units(self._margins),
        })

    @property
    def textbox_settings(self):
        return {
            'font': self.create_font(),
            'foreground': self['colour'],
            'background': self['background'],
            **self._units(self._spacing),
        }

    def create_font(self):
        if not self.font:
            return None
        try:
            return Font(**self.font)
        except RuntimeError:
            return self.font

    @property
    def _margins(self):
        return utils.filter_nonzero({
            'lmargin1': self.get('left', 0) + self.get('indent', 0),
            'lmargin2': self['left'],
            'rmargin': self['right'],
        })

    @property
    def _spacing(self):
        return {
            'spacing1': self['top'],
            'spacing2': self['line_spacing'],
            'spacing3': self['bottom'],
        }

    def _units(self, obj):
        return {k: self._unit(v) for k, v in obj.items()}

    def _unit(self, value):
        unit = self['unit']
        return f'{value}{unit[0]}' if self['unit'] else value

    @property
    def _border(self):
        if self['border']:
            return {'relief': 'ridge', 'borderwidth': 4}
        return {'relief': 'flat'}

    @property
    def _justify(self):
        justify = self['justification']
        return 'center' if justify == 'centre' else justify

    @property
    def _is_default(self):
        return self.name == 'default'

    @property
    def default_size(self):
        if self._is_default:
            return self.props.get('size', default.font['size'])
        try:
            return self.default_style.default_size
        except AttributeError:
            return self.props.get('size', default.font['size'])

    @default_size.setter
    def default_size(self, value):
        if self._is_default:
            self.props['size'] = value
        else:
            self.default_style.default_size = value

    def reset_size(self):
        self.default_size = self._unchanged['size']

    @property
    def default_font(self):
        return self.default_style.get('props', {}).get('font', default.font['font'])

    @property
    def _size(self):
        size = self['size'] or 100
        offset = self['offset']
        if not self._is_default:
            size = max(int(size * self.default_size / 100), 1)
        if offset and offset.endswith('script'):
            return size * 2 // 3
        return size if self.has_font else 0

    @property
    def _family(self):
        family = self['font'] or self.default_font
        return family if self.has_font else ''

    @property
    def _offset(self):
        offset = self['offset']
        if not offset or offset == 'baseline':
            return None
        size = self['size'] or self.default_size
        return (size // 3) if offset == 'superscript' else (-3 * size // 2)
