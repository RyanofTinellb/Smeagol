import re
import json
import tkinter as Tk
import tkinter.colorchooser as ColourChooser
import tkinter.messagebox as mb
import tkinter.simpledialog as sd
import tkinter.ttk as ttk
from tkinter.font import Font
from tkinter.font import families as font_families

from ....utils import ignored
from ...styles import Style


class StylesWindow(Tk.Frame):
    def __init__(self, styles, master=None, name=''):
        super().__init__(master)
        self.grid()
        self.master.protocol('WM_DELETE_WINDOW', self.cancel)
        self.master.title(f'{name} Styles')
        self.original = styles
        self.styles = styles.copy()
        self.styles_box(self).grid(
            row=0, column=0, columnspan=3, sticky='s', padx=10, pady=5)
        self.style_buttons(self).grid(row=1, column=0, padx=10)
        self.sample_box(self).grid(row=0, column=4, rowspan=3, columnspan=2, padx=10, pady=5)
        self.window_buttons(self).grid(row=4, column=5, padx=10, sticky='e')
        self.select_style()

    def style_buttons(self, master=None):
        frame = Tk.Frame(master)
        Tk.Button(frame, text='Edit', command=self.edit).grid(row=0, column=0)
        self.rename_btn = Tk.Button(frame, text='Rename', command=self.rename)
        self.rename_btn.grid(row=0, column=1)
        self.delete_btn = Tk.Button(frame, text='Delete', command=self.delete)
        self.delete_btn.grid(row=0, column=2, sticky='w')
        Tk.Button(frame, text='New', command=self.add).grid(row=0, column=3)
        return frame

    def styles_box(self, master=None):
        box = ttk.Combobox(master, values=self.styles.names)
        box.bind('<<ComboboxSelected>>', self.select_style)
        box.set('default')
        self.current = box
        return box

    def select_style(self, event=None):
        style = self.styles[self.current.get()]
        state = 'disabled' if style.name == 'default' else 'normal'
        self.delete_btn.config(state=state)
        self.rename_btn.config(state=state)
        font = style.Font
        box = self._sample
        box.tag_delete('sample')
        box.tag_add('sample', 1.0, 'end')
        box.tag_config('sample', font=font, **style.paragraph)

    def window_buttons(self, master=None):
        frame = Tk.Frame(master)
        button = Tk.Button(frame, text='Cancel', command=self.cancel)
        button.grid(row=0, column=0)
        button = Tk.Button(frame, text='OK', command=self.ok)
        button.grid(row=0, column=1)
        return frame

    def sample_box(self, master=None):
        box = Tk.Text(master, height=3, width=20)
        box.insert(Tk.INSERT, 'Sample', 'sample')
        box.config(state='disabled')
        self._sample = box
        return box

    def rename(self, event=None):
        style = self.current.get()
        name = sd.askstring(
            'Style Name', f'What is the new name of "{style}"?')
        if name and name not in self.styles:
            self.styles[style].name = name
            self.styles[name] = self.styles[style]
            self.styles.remove(style)
            self.current.config(values=self.styles.names)
            self.current.set(name)
            self.select_style()

    def edit(self, event=None):
        top = Tk.Toplevel()
        editor = StyleEditor(
            master=top, style=self.styles[self.current.get()])
        self.master.withdraw()
        self.wait_window(top)
        self.styles[self.current.get()] = editor.style
        self.select_style()
        self.master.deiconify()

    def add(self, event=None):
        name = sd.askstring('Style Name', 'What is the name of the new style?')
        if name and name not in self.styles:
            self.styles.add(name)
            self.current.config(values=self.styles.names)
            self.current.set(name)
            self.select_style()
            self.edit()

    def delete(self, event=None):
        style = self.current.get()
        message = f'Are you sure you wish to delete the style "{style}"?'
        if mb.askyesno('Delete', message):
            self.styles.remove(style)
            self.current.config(values=self.styles.name)
            self.current.set('default')
            self.select_style()

    def cancel(self):
        self.master.destroy()

    def ok(self):
        self.original.update(self.styles)
        self.cancel()


class StyleEditor(Tk.Frame):
    def __init__(self, master=None, style=None):
        super().__init__(master)
        self.master.title(style.name)
        self.grid()
        self.backup = style
        self.style = style.copy()
        self.disabled = 'disabled' if not self.style.block else ''
        self.spinners = []
        self.non_spinners = []
        self.units = 'points', 'millimetres', 'centimetres', 'inches'
        types = {str: Tk.StringVar, bool: Tk.BooleanVar,
                 float: Tk.DoubleVar, int: Tk.IntVar}
        for attr, value in self.style.items():
            if attr == 'unit':
                value = [v for v in self.units if v.startswith(value[0])][0]
            setattr(self, attr, types[type(value)](value=value))
        if self.style.name != 'default':
            self.font_frame(self).grid(row=0, column=0, rowspan=2, sticky='nw')
            self.sample_frame(self).grid(row=2, column=0, columnspan=2, padx=60)
            self.buttons_frame(self).grid(row=2, column=2, sticky='se')
            self.para_frame(self).grid(row=0, column=1, sticky='nw')
            self.options_frame(self).grid(row=0, column=2, sticky='nw')
            self.colour_frame(self).grid(row=1, column=1, sticky='nw')
        else:
            self.font_frame(self).grid(row=0, column=0)
            self.colour_frame(self).grid(row=1, column=0)
            self.sample_frame(self).grid(row=2, column=0, padx=20)
            self.buttons_frame(self).grid(row=2, column=1, sticky='s')
    
    def options_frame(self, master=None):
        frame = ttk.LabelFrame(master, text='options')
        self.block_frame(frame).grid(row=0, column=0, sticky='w')
        self.key_frame(frame).grid(row=1, column=0, sticky='w')
        self.tags_frame(frame).grid(row=2, column=0, sticky='w')
        attrs = 'language', 'hyperlink'
        for row, attr in enumerate(attrs, start=3):
            var = getattr(self, attr)

            def handler(attr=attr):
                self.update_config(attr)
            btn = Tk.Checkbutton(frame, text=attr, var=var, command=handler)
            btn.grid(row=row, column=0, sticky='w')
        return frame

    def key_frame(self, master=None):
        frame = Tk.Frame(master)
        Tk.Label(frame, text='key', justify='right').grid(row=0, column=0, sticky='e')
        box = Tk.Entry(frame, width=2, justify='center', textvariable=self.key)
        def handler(event=None):
            if event.keysym == 'Return':
                return 'break'
            if re.match(r'[a-zA-Z]', key := event.char):
                self.key.set(key)
            else:
                self.key.set('')
            self.update_config('key')
            return 'break'
        box.bind('<KeyPress>', handler)
        box.grid(row=0, column=1, padx=10)
        return frame

    def buttons_frame(self, master=None):
        frame = Tk.Frame(master)
        Tk.Button(frame, text='Cancel', command=self.cancel).grid(
            row=0, column=0)
        Tk.Button(frame, text='OK', command=self.ok).grid(
            row=0, column=1)
        return frame

    def tags_frame(self, master=None):
        frame = ttk.Labelframe(master, text='tags')
        self.tag_boxes = [Tk.Entry(frame, width=30) for _ in range(2)]
        for row, (entry, tag) in enumerate(zip(self.tag_boxes, self.style.tags)):
            entry.grid(row=row, column=0)
            entry.insert(0, tag)
        return frame

    def cancel(self):
        self.style = self.backup
        self.ok()

    def ok(self):
        with ignored(AttributeError):
            self.style.tags = [b.get() for b in self.tag_boxes]
            self.style.block = self.block_box.get()
        self.master.destroy()

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
                _, colour = ColourChooser.askcolor(
                    initialcolor=var.get(), parent=frame, title=name)
                if colour:
                    var.set(colour)
                    self.update_config(attr)
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
        families = sorted([''] + 
            [f for f in font_families() if not f.startswith('@')])

        def handler(*args):
            self.update_config('font')
        box = ttk.Combobox(master, width=20, values=families,
                           textvariable=self.font)
        box.bind('<<ComboboxSelected>>', handler)
        return box

    def size_box(self, master=None):
        def handler(*args):
            self.update_config('size')
        box = ttk.Spinbox(master, width=5, from_=1, to=72,
                          textvariable=self.size, command=handler)
        return box

    def styling_frame(self, master=None):
        frame = Tk.Frame(master)
        attrs = 'bold', 'italics', 'underline', 'strikethrough', 'border'
        for row, attr in enumerate(attrs, start=1):
            var = getattr(self, attr)

            def handler(attr=attr):
                self.update_config(attr)
            btn = Tk.Checkbutton(frame, text=attr, var=var, command=handler)
            btn.grid(row=row, column=0, sticky='w')
        return frame

    def offset_frame(self, master=None):
        frame = ttk.LabelFrame(master, text='offset')
        attrs = 'superscript', 'baseline', 'subscript'

        def handler(*args):
            self.update_config('offset')
        for row, attr in enumerate(attrs):
            Tk.Radiobutton(frame, text=attr, variable=self.offset,
                           value=attr, command=handler).grid(row=row, column=0, sticky='w')
        return frame

    def para_frame(self, master=None):
        frame = Tk.LabelFrame(master, text='paragraph')
        self.leftovers_frame(frame).grid(row=0, column=0)
        self.direction_frame(frame).grid(row=0, column=1)
        self.units_frame(frame).grid(row=1, column=0, columnspan=2)
        return frame

    def block_frame(self, master=None):
        frame = Tk.Frame(master)
        Tk.Label(frame, text='block').grid(row=0, column=0)

        self.block_box = Tk.Entry(frame, width=30)
        self.block_box.grid(row=0, column=1)
        self.block_box.insert(0, self.block.get())
        self.block_box.bind('<KeyRelease>', self.set_para_element_state)
        return frame

    def enable_para_elements(self):
        for _, elt in self.spinners:
            elt.config(state='normal')
        for _, elt in self.non_spinners:
            elt.config(state='readonly')

    def disable_para_elements(self):
        for _, elt in self.spinners + self.non_spinners:
            elt.config(state='disabled')

    def set_para_element_state(self, event=None):
        if self.block_box.get():
            self.enable_para_elements()
        else:
            self.disable_para_elements()

    def direction_frame(self, master=None):
        frame = ttk.LabelFrame(
            master, text='margins and padding', padding=10)
        spinners = (('left', 1, 0), ('top', 0, 1),
                    ('right', 1, 2), ('bottom', 2, 1))
        for name, row, column in spinners:
            spinner = self.spinner(frame, name)
            spinner.grid(row=row, column=column)
            self.spinners.append((name, spinner))
        return frame

    def spinner(self, master, name):
        decimals = self.unit.get()[0] in 'ci'
        var = getattr(self, name)

        def handler(name=name):
            self.update_config(name)
        spinner = ttk.Spinbox(master, width=5, from_=0, to=40,
                              increment=0.1 if decimals else 1,
                              textvariable=var, command=handler, state=self.disabled or 'normal')
        return spinner

    def leftovers_frame(self, master=None):
        frame = Tk.Frame(master, padx=10)
        spinners = (('indent', 0, 1), ('line_spacing', 1, 1))
        for name, row, column in spinners:
            spinner = self.spinner(frame, name)
            spinner.grid(row=row, column=column)
            self.spinners.append((name, spinner))
        labels = 'indent', 'line spacing', 'justification'
        for row, name in enumerate(labels):
            ttk.Label(frame, text=name, padding=(5, 0)).grid(
                row=row, column=0, sticky='e')
        self.justify(frame).grid(row=2, column=1)
        return frame

    def justify(self, master=None):
        def handler(*args):
            self.update_config('justification')
        box = ttk.Combobox(master, width=6, values=('left', 'centre', 'right'),
                           textvariable=self.justification, state=self.disabled or 'readonly')
        box.bind('<<ComboboxSelected>>', handler)
        self.non_spinners.append(('justify', box))
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
        box.config(font='Calibri 18', wrap='word')
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
            self.update_config('unit')
        selector = ttk.Combobox(frame, state=self.disabled or 'readonly',
                                textvariable=self.unit, values=self.units)
        selector.bind('<<ComboboxSelected>>', handler)
        selector.grid(row=0, column=1)
        self.non_spinners.append(('unit', selector))
        return frame

    def update_config(self, attr):
        variable = getattr(self, attr)
        box = self.sample
        setattr(self.style, attr, variable.get())
        self.font_.config(**self.style._font)
        box.tag_configure('default', font=self.font_,
                          **self.style.paragraph)
        if attr == 'unit':
            self.settle_spinners()

    def settle_spinners(self):
        decimals = self.unit.get()[0] in 'ci'
        rounding = float if decimals else int
        var_type = Tk.DoubleVar if decimals else Tk.IntVar
        for attr, spinner in self.spinners:
            var = var_type()
            var.set(rounding(getattr(self, attr).get()))
            setattr(self, attr, var)
            spinner.config(format='%.1f' if decimals else '',
                           increment=0.1 if decimals else 1,
                           from_=rounding(0), to=rounding(40),
                           textvariable=var)
