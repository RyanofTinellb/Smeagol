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

from .tag import Tag
from ...utilities import errors
from ...utilities.defaults import default

DEFAULTS = default.style


class Style(Tag):
    def __init__(self, tags=None, props=None, defaults=None):
        super().__init__(tags)
        self.props = props or {}
        self.defaults = defaults or default.style

    @property
    def default_size(self):
        return self.defaults.get("props", {}).get("size", 18)

    def __getitem__(self, attr):
        try:
            return self.props.get(attr, self.defaults[attr])
        except KeyError as e:
            raise errors.throw_error(KeyError, self, attr) from e

    def get(self, attr, default_value):
        try:
            return self[attr]
        except KeyError:
            return default_value

    @property
    def font(self):
        return {
            "family": self["font"],
            "size": self._size,
            "weight": self._bold,
            "slant": self._italics,
            "underline": self["underline"],
            "overstrike": self["strikethrough"],
        }

    @property
    def _bold(self):
        return "bold" if self["bold"] else "normal"

    @property
    def _italics(self):
        return "italic" if self["italics"] else "roman"

    @property
    def paragraph(self):
        return dict(
            justify=self._justify,
            offset=self._offset,
            **self.textbox_settings,
            **self._border,
            **self._units(self._margins),
        )

    @property
    def textbox_settings(self):
        return dict(
            font=self.create_font(),
            foreground=self["colour"],
            background=self["background"],
            **self._units(self._spacing),
        )

    def create_font(self):
        try:
            return Font(**self.font)
        except RuntimeError:
            return self.font

    @property
    def _margins(self):
        return dict(
            lmargin1=self["left"] + self["indent"],
            lmargin2=self["left"],
            rmargin=self["right"],
        )

    @property
    def _spacing(self):
        return dict(
            spacing1=self["top"],
            spacing2=self["line_spacing"],
            spacing3=self["bottom"],
        )

    def _units(self, obj):
        return {k: self._unit(v) for k, v in obj.items()}

    def _unit(self, value):
        unit = self["unit"]
        return f"{value}{unit[0]}" if self["unit"] else value

    @property
    def _border(self):
        if self["border"]:
            return {"relief": "ridge", "borderwidth": 4}
        return {"relief": "flat"}

    @property
    def _justify(self):
        justify = self["justify"]
        return "center" if justify == "centre" else justify

    @property
    def _size(self):
        size = self["size"]
        offset = self["offset"]
        if isinstance(size, str):
            size = max(int(size) + self.default_size, 1)
        if offset.endswith("script"):
            return size * 2 // 3
        return size

    @property
    def _offset(self):
        offset = self["offset"]
        if offset == "baseline":
            return 0
        size = self["size"]
        return (size // 3) if offset == "superscript" else (-3 * size // 2)
