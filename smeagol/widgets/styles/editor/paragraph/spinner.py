from tkinter import ttk


class Spinner(ttk.Spinbox):
    def __init__(self, parent, style, var):
        self.style = style
        self.unit = self.style.unit
        self.var = var
        super().__init__(parent, **self.options)

    def settle(self):
        self.config(**self.options)

    @property
    def decimals(self):
        return self.unit.get()[0] in 'ci'

    @property
    def rounding(self):
        return float if self.decimals else int

    @property
    def options(self):
        return {
            'width': 5,
            'format': '%.1f' if self.decimals else '',
            'from_': self.rounding(0),
            'to': self.rounding(40),
            'increment': 0.1 if self.decimals else 1,
            'textvariable': self.var,
            'state': self.style.state.get() or 'normal'}
