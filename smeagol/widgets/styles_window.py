from collections import namedtuple
from copy import deepcopy
from tkinter.colorchooser import askcolor as askcolour
from tkinter.font import families as font_families
from tkinter.font import Font
import tkinter as Tk
from tkinter.ttk import Notebook, Combobox
Tk.Notebook = Notebook
Tk.Combobox = Combobox

Widget = namedtuple('Widget', 'widget command text')

class StylesWindow(Tk.Toplevel):
    def __init__(self, styles=None, master=None):
        super().__init__(master)
        self.styles = styles or []
        self.notebook = Tk.Notebook(self)
        font_frame = Tk.Frame(self.notebook)
        paragraph_frame = Tk.Frame(self.notebook)
        self.notebook.add(font_frame)
        self.notebook.add(paragraph_frame)
        for frame in (font_frame, paragraph_frame):
            for column, label in enumerate(('Start Tag', 'End Tag', 'Name')):
                label = Tk.Label(frame, text=label, width=15)
                label.grid(row=0, column=column, sticky='we')
        font_frame.row = para_frame.row = 0
        for style in self.styles:
            frame = font_frame if style.font else paragraph_frame
            for column, box in enumerate(self.input_row(style)):
                box.widget.grid(row=frame.row, column=column, sticky='ns')
                frame.row += 1

    def edit(self, style):
        self.open_format_window(style)

    def new(self):
        style = blank_style
        self.open_format_window(style)

    def open_format_window(self, style):
        window = FormatWindow(style)
        self.master.withdraw()
        self.wait_window(window)

    def input_row(self, style):
        tags = style.get('tags', ('', ''))
        tags = [self.tag_box(tag) for tag in tags]
        name_box = self.name_box(style)
        edit_button = self.edit_button(style)
        name_box.widget.bind('<Double-Button-1>', edit_button['command'])
        return tags + [name_box, edit_button]

    def edit_button(self, style):
        def handler(event=None, style=style):
            self.edit(style)
            return 'break'
        btn = Tk.Button(self, text='Edit', command=handler)
        return Widget(widget=btn, command=handler)

    def tag_box(self, tag):
        text = Tk.StringVar()
        text.set(tag.replace('\n', '\\n'))
        entry = Tk.Entry(self, width=15, textvariable=text)
        return Widget(widget=entry, text=text)

    def name_box(self, style):
        font = Font(**style.get('font', {}))
        box = Tk.Text(self, width=50, height=2)
        box.tag_config('x', font=font, **style.get('paragraph', {}))
        box.insert(1.0, style.get('name', ''), ('x'))
        return Widget(widget=box)


class FormatWindow(Tk.Toplevel):
    def __init__(self, style, master=None):
        super().__init__(master)
        self.notebook = Tk.Notebook(self)
        self.notebook.pack()
        self.notebook.add(FontMenu(self.notebook, style), text='Font')
        self.notebook.add(ParagraphMenu(
            self.notebook, style), text='Paragraph')


class FontMenu(Tk.Frame):
    def __init__(self, master=None, style=None):
        super().__init__(master)
        self.style = deepcopy(style)
        for elt in 'frames', 'labels', 'buttons', 'colours', 'fonts', 'checks', 'radios':
            try:
                getattr(self, f'ready_{elt}')(style)
            except TypeError:
                getattr(self, f'ready_{elt}')()

    def ready_frames(self):
        self.variant = Tk.LabelFrame(self)
        self.variant.grid(row=2, column=0)
        self.script = Tk.LabelFrame(self)
        self.script.grid(row=2, column=1)
    
    def ready_buttons(self):
        pass

    def ready_fonts(self):
        fonts = sorted(
            list(filter(lambda x: not x.startswith('@'), font_families())))
        font_entry = Tk.Combobox(self, values=fonts)
        font_entry.grid(row=1, column=0)

    def ready_colours(self, style):
        foreground = dict(name='colour', attr='foreground')
        background = dict(name='background', attr='background')
        for column, elt in enumerate((foreground, background), start=2):
            elt['colour'] = style['paragraph'][elt['attr']]
            button = Tk.Button(self, background=elt['colour'])

            def command(elt=elt, button=button):
                default, title, attr = [elt[attr]
                                        for attr in ('colour', 'name', 'attr')]
                colour = askcolour(default, title=title)
                button.configure(background=colour)
                style['paragraph'][attr] = colour
            button.configure(command=command)
            button.grid(row=1, column=column)

    def ready_labels(self):
        attrs = ('name', 'master', 'row', 'column')
        Label = namedtuple('Label', attrs)
        for label in (Label('font', self, 0, 0), Label('size', self, 0, 1),
                      Label('colour', self, 0, 2),
                      Label('background', self, 0, 3),
                      Label('bold', self.variant, 0, 1),
                      Label('italics', self.variant, 1, 1),
                      Label('underline', self.variant, 2, 1),
                      Label('strikethrough', self.variant, 3, 1),
                      Label('superscript', self.script, 0, 1),
                      Label('baseline', self.script, 1, 1),
                      Label('subscript', self.script, 2, 1)):
            name, master, row, column = [getattr(label, attr) for attr in attrs]
            label = Tk.Label(master, text=name)
            label.grid(row=row, column=column)


class ParagraphMenu(Tk.Frame):
    def __init__(self, master=None, style=None):
        super().__init__(master)
