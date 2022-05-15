import tkinter as tk


class Styling(tk.Frame):
    def __init__(self, parent, style):
        super().__init__(parent)
        self.style = style
        for row, (attr, var) in enumerate(self.buttons, start=1):
            btn = tk.Checkbutton(self, text=attr, var=var)
            btn.grid(row=row, column=0, sticky='w')

    @property
    def buttons(self):
        return (
            ('bold', self.style.bold),
            ('italics', self.style.italics),
            ('underline', self.style.underline),
            ('strikethrough', self.style.strikethrough),
            ('border', self.style.border)
        )
