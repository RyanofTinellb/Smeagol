import tkinter as Tk
import tkinter.ttk as ttk
import tkinter.colorchooser as ColourChooser
from tkinter.font import Font
from tkinter.font import families as font_families


class StylesWindow(Tk.Frame):
    def __init__(self, styles, master=None):
        super().__init__(master)
        self.styles = [s.copy() for s in styles]
        notebook = ttk.Notebook(self)
        notebook.pack(side=Tk.LEFT, expand=True, fill=Tk.BOTH)
        frame = StyleFrame(notebook, self.style_group('default')[0])
        notebook.add(frame, text='default')

    def style_group(self, name):
        return [s for s in self.styles if s.group == name]


class StyleFrame(Tk.Frame):
    def __init__(self, master=None, style=None):
        super().__init__(master)
        self.style = style.copy()
        self.is_disabled = 'disabled' if self.style.group == 'font' else 'readonly'
        self.spinners = []
        self.units = 'points', 'millimetres', 'centimetres', 'inches'
        types = {str: Tk.StringVar, bool: Tk.BooleanVar,
                 float: Tk.DoubleVar, int: Tk.IntVar}
        for attr, value in self.style.items():
            setattr(self, attr, types[type(value)]())
        for attr, value in self.style.items():
            if attr == 'unit':
                value = [v for v in self.units if v.startswith(value[0])][0]
            getattr(self, attr).set(value)
        self.font_frame(self).grid(row=0, column=0, rowspan=2, sticky='w')
        self.para_frame(self).grid(row=0, column=1, sticky='nw')
        self.colour_frame(self).grid(row=1, column=1, sticky='nw')
        self.sample_frame(self).grid(row=2, column=0, columnspan=2)

    def colour_frame(self, master=None):
        frame = ttk.LabelFrame(master, text='colour')
        selectors = ('text', 'colour'), ('background', 'background')
        for col, (name, attr) in enumerate(selectors):
            var = getattr(self, attr)
            ttk.Label(frame, text=name, padding=(
                15, 0, 5, 0)).grid(row=0, column=2*col)
            btn = Tk.Button(frame, background=var.get(),
                            width=2)

            def handler(name=name, attr=attr, var=var, frame=frame, btn=btn):
                rgb, colour = ColourChooser.askcolor(
                    initialcolor=var.get(), parent=frame, title=name)
                if colour:
                    var.set(colour)
                    self.update_config(attr, var)
                    btn.config(background=colour)
            btn.grid(row=0, column=2*col+1)
            btn.config(command=handler)
        return frame

    def font_frame(self, master=None):
        frame = ttk.LabelFrame(master, text='font')
        self.family_box(frame).grid(row=0, column=0)
        self.size_box(frame).grid(row=0, column=1)
        self.styling_frame(frame).grid(row=1, column=0, sticky='w')
        self.offset_frame(frame).grid(row=1, column=1)
        return frame

    def family_box(self, master=None):
        families = sorted(
            [f for f in font_families() if not f.startswith('@')])

        def handler(*args):
            self.update_config('font', self.font)
        box = ttk.Combobox(master, width=20, values=families,
                           textvariable=self.font)
        box.bind('<<ComboboxSelected>>', handler)
        return box

    def size_box(self, master=None):
        def handler(*args):
            self.update_config('size', self.size)
        box = ttk.Spinbox(master, width=5, from_=1, to=72,
                          textvariable=self.size, command=handler)
        return box

    def styling_frame(self, master=None):
        frame = Tk.Frame(master)
        attrs = 'bold', 'italics', 'underline', 'strikethrough', 'border'
        for row, attr in enumerate(attrs, start=1):
            var = getattr(self, attr)

            def handler(attr=attr, var=var):
                self.update_config(attr, var)
            btn = Tk.Checkbutton(frame, text=attr, var=var, command=handler)
            btn.grid(row=row, column=0, sticky='w')
        return frame

    def offset_frame(self, master=None):
        frame = ttk.LabelFrame(master, text='offset')
        attrs = 'superscript', 'baseline', 'subscript'

        def handler(*args):
            self.update_config('offset', self.offset)
        for row, attr in enumerate(attrs):
            Tk.Radiobutton(frame, text=attr, variable=self.offset,
                           value=attr, command=handler).grid(row=row, column=0, sticky='w')
        return frame

    def para_frame(self, master=None):
        frame = Tk.LabelFrame(master, text='paragraph')
        self.direction_frame(frame).grid(row=0, column=1)
        self.leftovers_frame(frame).grid(row=0, column=0)
        self.units_frame(frame).grid(row=1, column=0, columnspan=2)
        return frame

    def direction_frame(self, master=None):
        frame = ttk.LabelFrame(
            master, text='margins and padding', padding=10)
        spinners = (('left', 1, 0), ('top', 0, 1),
                    ('right', 1, 2), ('bottom', 2, 1))
        self.spinners += [self.spinner(frame, *s) for s in spinners]
        return frame

    def spinner(self, master, name, row, column):
        decimals = self.unit.get()[0] in 'ci'
        rounding = float if decimals else int
        var = getattr(self, name)

        def handler(name=name, var=var):
            self.update_config(name, var)
        spinner = ttk.Spinbox(master, width=5, from_=0, to=40,
                              increment=0.1 if decimals else 1,
                              textvariable=var, command=handler, state=self.is_disabled)
        spinner.grid(row=row, column=column)
        return spinner

    def leftovers_frame(self, master=None):
        frame = Tk.Frame(master, padx=10)
        spinners = (('indent', 0, 1), ('line_spacing', 1, 1))
        self.spinners += [self.spinner(frame, *s) for s in spinners]
        labels = 'indent', 'line spacing', 'justification'
        for row, name in enumerate(labels):
            ttk.Label(frame, text=name, padding=(5, 0)).grid(
                row=row, column=0, sticky='e')
        self.justify(frame).grid(row=2, column=1)
        return frame

    def justify(self, master=None):
        def handler(*args):
            self.update_config('justification', self.justification)
        box = ttk.Combobox(master, width=6, values=('left', 'centre', 'right'),
                           textvariable=self.justification, state=self.is_disabled)
        box.bind('<<ComboboxSelected>>', handler)
        return box

    def sample_frame(self, master=None):
        frame = Tk.LabelFrame(master, text='sample')
        self.sample = self.sample_box(frame)
        self.sample.pack()
        return frame

    def sample_box(self, master=None):
        box = Tk.Text(master, height=5, width=30)
        self.font_ = Font(box, **self.style._font)
        font = Font(box, **self.style._font)
        box.tag_configure('default', font=self.font_, **
                          self.style.paragraph)
        box.config(font=font, wrap='word', **self.style.config)
        lorem = ('Lorem ipsum dolor sit amet, consectetur adipiscing elit, '
                 'sed do eiusmod tempor incididunt ut labore et dolore '
                 'magna aliqua. Ut enim ad minim veniam, quis nostrud '
                 'exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.')
        box.insert(1.0, lorem, 'default')
        return box

    def units_frame(self, master=None):
        frame = Tk.Frame(master)
        ttk.Label(frame, text='units').grid(row=0, column=0)

        def handler(*args):
            self.update_config('unit', self.unit)
        selector = ttk.Combobox(frame, state='readonly',
                                textvariable=self.unit, values=self.units)
        selector.bind('<<ComboboxSelected>>', handler)
        selector.grid(row=0, column=1)
        return frame

    def update_config(self, name, variable):
        box = self.sample
        setattr(self.style, name, variable.get())
        self.font_.config(**self.style._font)
        box.tag_configure('default', font=self.font_,
                          **self.style.paragraph)
        if name == 'unit':
            self.settle_spinners()

    def settle_spinners(self):
        decimals = self.unit.get()[0] in 'ci'
        rounding = float if decimals else int
        for spinner in self.spinners:
            spinner.config(format='%.1f' if decimals else '',
                           increment=0.1 if decimals else 1,
                           from_=rounding(0),
                           to=rounding(40))
        attrs = 'line_spacing', 'indent', 'top', 'left', 'bottom', 'right'
        for attr in attrs:
            var = getattr(self, attr)
            var.set(rounding(var.get()))
