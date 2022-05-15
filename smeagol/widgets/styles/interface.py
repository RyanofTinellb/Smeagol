import tkinter as tk

types = {int: tk.IntVar,
         float: tk.DoubleVar,
         str: tk.StringVar,
         bool: tk.BooleanVar}

class Interface:
    def __init__(self, style):
        self.style = style
        for attr, value in style.items():
            var = self.make_var(value, attr)
            var.trace_add('write', self.changed)
            setattr(self, attr, var)
        self.state = self.make_var(self._state, attr)
    
    def __getattr__(self, attr):
        if attr in {'_font', 'paragraph', 'name', 'items', 'copy'}:
            return getattr(self.style, attr)
        return getattr(super(), attr)
    
    @property
    def _state(self):
        return '' if self.style.block else 'disabled'

    def changed(self, attr, *_):
        setattr(self.style, attr, getattr(self, attr).get())

    def make_var(self, value, attr):
        try:
            return types[type(value)](value=value, name=attr)
        except KeyError:
            type_ = value.__class__.__name__
            raise TypeError(f'Value must be int, float, str or bool, not {type_}')
    
