import tkinter as Tk


class Block(Tk.Frame):
    def __init__(self, parent, style):
        super().__init__(parent)
        self.style = style
        Tk.Label(self, text='block').grid(row=0, column=0)
        self.Box.grid(row=0, column=1)

    @property
    def Box(self):
        return Tk.Entry(self, **self.box_options)
    
    @property
    def box_options(self):
        return dict(
            width=30,
            textvariable=self.style.block)