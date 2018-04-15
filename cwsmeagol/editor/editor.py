import Tkinter as Tk
import tkFont
from itertools import izip
from cwsmeagol.utils import ignored


class Editor(Tk.Frame, object):
    def __init__(self, master=None):
        super(Editor, self).__init__(master)
        self.headings = 2
        self.textboxes = 1
        self.buttonframe = Tk.Frame(master)
        self.headingframe = Tk.Frame(self.buttonframe)
        self.textframe = Tk.Frame(master)
        self.row = 0
        self.font = tkFont.Font(family='Calibri', size=18)
        self.top = self.winfo_toplevel()
        self.ready()

    def ready(self):
        for obj in ['headings', 'menus', 'labels', 'radios', 'buttons', 'textboxes']:
            getattr(self, 'ready_' + obj)()
        self.place_widgets()
        self.top.state('zoomed')

    def ready_headings(self):
        master = self.headingframe
        self.headings = [Tk.Entry(master) for _ in xrange(self.headings)]

    def ready_menus(self):
        """
        Ready the top menu.
        """
        self.menu = Tk.Menu(self.top)
        menu_commands = [('Site', [('Open', self.site_open),
                                   ('Save', self.save_site),
                                   ('Save _As', self.save_site_as),
                                   ('Open in _Browser', self.open_in_browser),
                                   ('P_roperties', self.site_properties),
                                   ('S_ee All', self.list_pages),
                                   ('Publish _WholePage', self.save_wholepage),
                                   ('Publish All', self.site_publish)]),
                         ('Markdown', [('Load', self.markdown_load),
                                       ('Refresh', self.markdown_refresh),
                                       ('Check', self.markdown_check),
                                       ('Change to _Tkinter',
                                        self.html_to_tkinter),
                                       ('Change to Ht_ml', self.tkinter_to_html),
                                       ('Open as _Html', self.markdown_open)]
                          )]
        for menu in menu_commands:
            submenu = Tk.Menu(self.menu, tearoff=0)
            label, options = menu
            self.menu.add_cascade(label=label, menu=submenu)
            for option in options:
                label, command = option
                underline = label.find('_')
                underline = 0 if underline == -1 else underline
                label = label.replace('_', '')
                submenu.add_command(label=label, command=command,
                                    underline=underline)
                submenu.bind(
                    '<KeyPress-{0}>'.format(label[underline]), command)

    def ready_labels(self):
        master = self.buttonframe
        self.information = Tk.StringVar()
        self.info_label = Tk.Label(
            master=master, textvariable=self.information, font=('Arial', 14))
        # blanklabel has enough height to push all other widgets to the top
        #   of the window.
        self.current_style = Tk.StringVar()
        self.current_style.set('')
        self.style_label = Tk.Label(
            master=master, textvariable=self.current_style, font=('Arial', 12))
        self.blank_label = Tk.Label(master=master, height=1000)

    def ready_radios(self):
        master = self.buttonframe
        translator = self.translator
        settings = translator.languages.items()
        number = translator.number
        self.radios = [Tk.Radiobutton(master) for _ in xrange(number)]
        settings = zip(self.radios, settings)
        for radio, (code, language) in settings:
            radio.configure(text=language().name, variable=self.languagevar,
                            value=code, command=self.change_language)

    def ready_buttons(self):
        master = self.buttonframe
        commands = self.load, self.save_page
        self.save_text = Tk.StringVar()
        self.load_button = Tk.Button(master, text='Load', command=commands[0])
        self.save_button = Tk.Button(master, command=commands[1],
                                     textvariable=self.save_text)
        self.buttons = [self.load_button, self.save_button]

    def ready_textboxes(self):
        master = self.textframe
        number = self.textboxes
        font = self.font
        self.textboxes = [Tk.Text(master, height=1, width=1, wrap=Tk.WORD,
                                  undo=True, font=font) for _ in xrange(number)]
        commands = [
            ('<MouseWheel>', self.scroll_textbox),
            ('<Control-MouseWheel>', self.change_fontsize),
            ('<Control-0>', self.reset_fontsize),
            ('<Control-a>', self.select_all),
            ('<Control-c>', self.copy_text),
            ('<Control-d>', self.add_heading),
            ('<Control-D>', self.remove_heading),
            ('<Control-v>', self.paste_text),
            ('<Control-x>', self.cut_text),
            ('<Control-BackSpace>', self.backspace_word),
            ('<Control-Delete>', self.delete_word),
            (('<Control-Up>', '<Control-Down>'), self.move_line),
            ('<Control-K>', self.delete_line),
            ('<Alt-d>', self.go_to_heading)
        ]
        self.add_commands('Text', commands)
        for textbox in self.textboxes:
            textbox.bind('<KeyPress>', self.edit_text_changed)
            textbox.bind('<Any-Button>', self.edit_text_changed)
            self.ready_scrollbar(textbox)
            for (name, style) in self.text_styles:
                textbox.tag_config(name, **style)

    def reset_textboxes(self):
        for textbox in self.textboxes:
            textbox.edit_modified(False)
            textbox.config(font=self.font)
            for (name, style) in self.text_styles:
                textbox.tag_config(name, **style)

    def ready_scrollbar(self, textbox):
        scrollbar = Tk.Scrollbar(self.textframe)
        scrollbar.pack(side=Tk.RIGHT, fill=Tk.Y)
        scrollbar.config(command=textbox.yview)
        textbox.config(yscrollcommand=scrollbar.set)

    def add_commands(self, tkclass, commands):
        for (keys, command) in commands:
            if isinstance(keys, basestring):
                self.bind_class(tkclass, keys, command)
            else:
                for key in keys:
                    self.bind_class(tkclass, key, command)

    @property
    def text_styles(self):
        (strong,
         em,
         underline,
         small_caps,
         highlulani,
         example,
         example_no_lines) = iter([self.font.copy() for _ in xrange(7)])
        strong.configure(weight='bold')
        em.configure(slant='italic')
        underline.configure(underline=True, family='Calibri')
        small_caps.configure(
            size=small_caps.actual(option='size') - 3,
            family='Algerian')
        highlulani.configure(
            size=highlulani.actual(option='size') + 3,
            family='Lulani')
        example.configure(size=-1)
        return [
            ('example', {'lmargin1': '2c', 'spacing1': '5m', 'font': example}),
            ('example-no-lines', {'lmargin1': '2c', 'font': example}),
            ('strong', {'font': strong}),
            ('em', {'font': em}),
            ('small-caps', {'font': small_caps}),
            ('link', {'foreground': 'blue', 'font': underline}),
            ('high-lulani', {'font': highlulani})
        ]

    def modify_fontsize(self, size):
        self.font.config(size=size)
        for textbox in self.textboxes:
            textbox.config(font=self.font)
            for (name, style) in self.text_styles:
                textbox.tag_config(name, **style)

    def change_fontsize(self, event):
        sign = 1 if event.delta > 0 else -1
        size = self.font.actual(option='size') + sign
        self.modify_fontsize(size)
        return 'break'

    def reset_fontsize(self, event):
        self.modify_fontsize(18)
        return 'break'

    def go_to(self, position):
        self.textboxes[0].mark_set(Tk.INSERT, position)
        self.textboxes[0].see(Tk.INSERT)

    def fill_headings(self, entries):
        while len(self.headings) < len(entries):
            self.add_heading()
        while len(self.headings) > len(entries):
            self.remove_heading()
        for heading, entry in zip(self.headings, entries):
            self.replace(heading, entry)

    def place_widgets(self):
        """
        Place all widgets in GUI window.
        Stack the textboxes on the right-hand side, taking as much
            room as possible.
        Stack the heading boxes, the buttons, radiobuttons and a
            label in the top-left corner.
        """
        self.top['menu'] = self.menu
        self.pack(expand=True, fill=Tk.BOTH)
        self.buttonframe.pack(side=Tk.LEFT)
        self.headingframe.grid(row=0, column=0, columnspan=2, sticky=Tk.N)
        self.textframe.pack(side=Tk.LEFT, expand=True, fill=Tk.BOTH)
        for heading in self.headings:
            heading.grid(column=0, columnspan=2, sticky=Tk.N)
        row = 1
        for i, button in enumerate(self.buttons):
            button.grid(row=row, column=i)
        row += 1
        self.style_label.grid(row=row, column=0, columnspan=2)
        row += 1
        for radio in self.radios:
            radio.grid(row=row, column=0, columnspan=2)
            row += 1
        for textbox in self.textboxes:
            textbox.pack(side=Tk.TOP, expand=True, fill=Tk.BOTH)
            row += 1
        self.info_label.grid(row=row, column=0, columnspan=2)
        self.blank_label.grid(row=row + 1, column=0, columnspan=2)

    def add_heading(self):
        if len(self.headings) < 10:
            heading = Tk.Entry(self.headingframe)
            heading.grid(column=0, columnspan=2, sticky=Tk.N)
            self.headings.append(heading)
        return 'break'

    def remove_heading(self, event=None):
        if len(self.headings) > 1:
            heading = self.headings.pop()
            heading.destroy()
        return 'break'

    def replace(self, widget, text):
        """
        Clears textbox and inserts text
        """
        try:  # textbox
            position = widget.index(Tk.INSERT)
            widget.delete(1.0, Tk.END)
            widget.insert(1.0, text)
            widget.mark_set(Tk.INSERT, position)
            widget.mark_set(Tk.CURRENT, position)
            widget.see(Tk.INSERT)
        except Tk.TclError:  # heading
            widget.delete(0, Tk.END)
            widget.insert(0, text)

    def clear_interface(self):
        for heading in self.headings:
            heading.delete(0, Tk.END)
        for textbox in self.textboxes:
            textbox.delete(1.0, Tk.END)
        self.information.set('')
        self.go_to_heading()

    def go_to_heading(self, event=None):
        """
        Move focus to the heading and select all the text therein
        """
        with ignored(IndexError):
            heading = self.headings[0]
            heading.focus_set()
            heading.select_range(0, Tk.END)
        return 'break'

    def window(self, current, direction):
        textbox = self.textboxes[(self.textboxes.index(event.widget) - 1)]
        textbox.focus_set()
        self.update_wordcount(widget=textbox)
        return 'break'

    def edit_text_changed(self, event):
        """
        Notify the user that the edittext has been changed.
        Activates after each keypress or mouseclick
        Deactivates after a save or a load action.
        """
        cancelkeys = ['Left', 'Right', 'Up', 'Down', 'Return']
        self.update_wordcount(event)
        if event.keysym.startswith('Control_'):
            event.widget.edit_modified(False)
        elif event.keysym in cancelkeys or event.num == 1:
            event.widget.edit_modified(False)
            event.widget.tag_remove(self.current_style.get(), Tk.INSERT)
            self.current_style.set('')
        elif event.widget.edit_modified():
            self.save_text.set('*Save')
            event.widget.tag_add(self.current_style.get(),
                                 Tk.INSERT + '-1c', Tk.INSERT)

    def scroll_textbox(self, event):
        for textbox in self.textboxes:
            textbox.yview_scroll(-1 * (event.delta / 20), Tk.UNITS)
        return 'break'

    @staticmethod
    def select_all(event):
        event.widget.tag_add('sel', '1.0', 'end')
        return 'break'

    def backspace_word(self, event):
        widget = event.widget
        get = widget.get
        if get(Tk.INSERT + '-1c') in '.,;:?! ':
            correction = '-2c wordstart'
        elif get(Tk.INSERT) in ' ':
            correction = '-1c wordstart -1c'
        else:
            correction = '-1c wordstart'
        widget.delete(Tk.INSERT + correction, Tk.INSERT)
        self.update_wordcount(event)
        return 'break'

    def delete_word(self, event):
        widget = event.widget
        get = widget.get
        if (
            get(Tk.INSERT + '-1c') in ' .,;:?!\n' or
            widget.compare(Tk.INSERT, '==', '1.0')
        ):
            correction = ' wordend +1c'
        elif get(Tk.INSERT) == ' ':
            correction = '+1c wordend'
        elif get(Tk.INSERT) in '.,;:?!':
            correction = '+1c'
        else:
            correction = ' wordend'
        widget.delete(Tk.INSERT, Tk.INSERT + correction)
        self.update_wordcount(event)
        return 'break'

    def move_line(self, event):
        self.tkinter_to_tkinter(self._move_line, [event])

    def _move_line(self, event):
        if event.keysym == 'Up':
            direction = ' -1 lines'
            correction = ' -1c linestart'
        elif event.keysym == 'Down':
            direction = ' +1 lines'
            correction = ' lineend +1c'
        else:
            return 'break'
        textbox = event.widget
        position = textbox.index(Tk.INSERT)
        try:
            ends = (Tk.SEL_FIRST + ' linestart',
                    Tk.SEL_LAST + ' lineend +1c')
            text = textbox.get(*ends)
            selected = map(textbox.index, (Tk.SEL_FIRST, Tk.SEL_LAST))
        except Tk.TclError:
            ends = (Tk.INSERT + ' linestart',
                    Tk.INSERT + ' lineend +1c')
            text = textbox.get(*ends)
            selected = None
        textbox.delete(*ends)
        textbox.insert(Tk.INSERT + correction, text)
        if selected:
            textbox.tag_add('sel', *map(lambda x: x + direction, selected))
        textbox.mark_set(Tk.INSERT, position + direction)

    def delete_line(self, event=None):
        try:
            event.widget.delete(Tk.SEL_FIRST + ' linestart',
                                Tk.SEL_LAST + ' lineend +1c')
        except Tk.TclError:
            event.widget.delete(Tk.INSERT + ' linestart',
                                Tk.INSERT + ' lineend +1c')
        return 'break'

    def update_wordcount(self, event=None, widget=None):
        if event is not None:
            widget = event.widget
        text = widget.get(1.0, Tk.END)
        self.information.set(
            str(text.count(' ') + text.count('\n') - text.count(' | ')))

    def display(self, texts):
        for textbox, text in izip(self.textboxes, texts):
            self.replace(textbox, text)
        else:
            textbox.focus_set()
            self.update_wordcount(widget=textbox)
        self.html_to_tkinter()

    def html_to_html(self, function, args=(), kwargs={}):
        self.html_to_tkinter()
        function(*args, **kwargs)
        self.tkinter_to_html()

    def tkinter_to_tkinter(self, function, args=(), kwargs={}):
        self.tkinter_to_html()
        function(*args, **kwargs)
        self.html_to_tkinter()

    def copy_text(self, event):
        self.tkinter_to_tkinter(self._copy_text, [event.widget])
        return 'break'

    def cut_text(self, event):
        self.tkinter_to_tkinter(self._cut_text, [event.widget])
        return 'break'

    def paste_text(self, event):
        self.tkinter_to_tkinter(self._paste_text, [event.widget])
        return 'break'

    def _copy_text(self, textbox):
        with ignored(Tk.TclError):
            borders = (Tk.SEL_FIRST, Tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(textbox.get(*borders))
        return borders

    def _cut_text(self, textbox):
        textbox.delete(*self._copy_text(textbox))

    def _paste_text(self, textbox):
        with ignored(Tk.TclError):
            borders = (Tk.SEL_FIRST, Tk.SEL_LAST)
            textbox.delete(*borders)
        textbox.insert(Tk.INSERT, self.clipboard_get())

    def html_to_tkinter(self):
        count = Tk.IntVar()
        for textbox in self.textboxes:
            for (style, _) in self.text_styles:
                while True:
                    try:
                        if style.startswith('example'):
                            letter = 'e' if style.endswith('lines') else 'f'
                            start = textbox.search(
                                '\[[{0}]\]'.format(letter),
                                '1.0',
                                regexp=True,
                                count=count
                            )
                            end = '{0}+3c'.format(start)
                            text = textbox.get(start, end)
                            text = text[1] + ' '
                            textbox.delete(start, end)
                            textbox.insert(start, text)
                            textbox.tag_add(
                                style, start, '{0}+{1}c'.format(start, len(text)))
                        else:
                            start = textbox.search(
                                '<{0}>.*?</{0}>'.format(style),
                                '1.0',
                                regexp=True,
                                count=count
                            )
                            end = '{0}+{1}c'.format(start, count.get())
                            text = textbox.get(start, end)
                            text = text[(len(style) + 2):(-3 - len(style))]
                            textbox.delete(start, end)
                            textbox.insert(start, text)
                            textbox.tag_add(style, start,
                                            '{0}+{1}c'.format(start, len(text)))
                    except Tk.TclError:
                        break
        self.reset_textboxes()

    def tkinter_to_html(self):
        for textbox in self.textboxes:
            for (style, _) in self.text_styles:
                for end, start in izip(*[reversed(textbox.tag_ranges(style))] * 2):
                    if style.startswith('example'):
                        text = textbox.get(start, end)[0]
                        text = '[{0}]'.format(text)
                    else:
                        text = textbox.get(start, end)
                        text = '<{1}>{0}</{1}>'.format(text, style)
                    textbox.delete(start, end)
                    textbox.insert(start, text)

    @property
    def heading_contents(self):
        return map(lambda heading: heading.get(), self.headings)
