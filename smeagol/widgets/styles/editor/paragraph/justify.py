from tkinter import ttk


class Justify(ttk.Combobox):
    def __init__(self, parent, style):
        self.style = style
        super().__init__(parent, **self.options)
    
    @property
    def options(self):
        return dict(
            width=6,
            values=('left', 'centre', 'right'),
            textvariable=self.style.justification,
            state=self.style.state or 'readonly')

    @property
    def non_spinners(self):
        return [('justify', self)]
