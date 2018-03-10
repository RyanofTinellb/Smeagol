import Tkinter as Tk
import tkFont

class Widgets(object):
    def __init__(self, master, headings=2, textboxes=1, font=None):
        self.headings = headings
        self.textboxes = textboxes
        self.buttonframe = Tk.Frame(master)
        self.headingframe = Tk.Frame(self.buttonframe)
        self.textframe = Tk.Frame(master)
        self.row = 0
        self.save_text = Tk.StringVar()
        self.master = master or Tk.Tk(None)
        self.top = self.master.top
        size = self.master.fontsize or 14
        self.font = font or tkFont.Font(family='Calibri', size=size)

    def ready(self):
        for obj in ['headings', 'menus', 'labels', 'radios', 'buttons', 'textboxes']:
            getattr(self, 'ready_' + obj)()
        self.place_widgets()
        self.top.state('zoomed')

    def ready_headings(self):
        master = self.headingframe
        self.headings = [Tk.Entry(master) for _ in xrange(self.headings)]
        for heading in self.headings:
            for command in self.heading_commands:
                keys, command = command
                for key in keys:
                    heading.bind(key, command)

    @property
    def heading_commands(self):
        return [(['<Prior>', '<Next>'], self.master.scroll_headings),
                (['<Return>'], self.master.enter_headings)]

    def ready_menus(self):
        """
        ready the top menu.
        """
        self.menu = Tk.Menu(self.top)
        for menu in self.menu_commands:
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
                submenu.bind('<KeyPress-{0}>'.format(label[underline]), command)

    @property
    def menu_commands(self):
        return [('Site', [('Open', self.master.site_open),
                        ('Save', self.master.site_save),
                        ('Save _As', self.master.site_saveas),
                        ('Open in _Browser', self.master.open_in_browser),
                        ('P_roperties', self.master.site_properties),
                        ('S_ee All', self.master.list_pages),
                        ('Publish All', self.master.site_publish)]),
                ('Markdown', [('Load', self.master.markdown_load),
                              ('Refresh', self.master.markdown_refresh),
                              ('Check', self.master.markdown_check),
                              ('Open as _Html', self.master.markdown_open)]
                              )]

    def ready_labels(self):
        master = self.buttonframe
        self.information = Tk.StringVar()
        self.info_label = Tk.Label(master=master, textvariable=self.information, font=('Arial', 14))
        # blanklabel has enough height to push all other widgets to the top
        #   of the window.
        self.blank_label = Tk.Label(master=master, height=1000)

    def ready_radios(self):
        master = self.buttonframe
        translator = self.master.translator
        settings = translator.languages.items()
        number = translator.number
        self.radios = [Tk.Radiobutton(master) for _ in xrange(number)]
        settings = zip(self.radios, settings)
        for radio, (code, language) in settings:
            radio.configure(text=language().name, variable=self.master.language,
                                    value=code, command=self.master.change_language)

    def ready_buttons(self):
        master = self.buttonframe
        commands = self.button_commands
        self.load_button = Tk.Button(master, text='Load', command=commands[0])
        self.save_button = Tk.Button(master, command=commands[1],
        textvariable=self.save_text)
        self.buttons = [self.load_button, self.save_button]

    @property
    def button_commands(self):
        return self.master.load, self.master.save

    def ready_textboxes(self):
        master = self.textframe
        number = self.textboxes
        font = self.font
        self.textboxes = [Tk.Text(master, height=1, width=1, wrap=Tk.WORD,
                            undo=True, font=font) for _ in xrange(number)]
        for textbox in self.textboxes:
            scrollbar = Tk.Scrollbar(self.textframe)
            scrollbar.pack(side=Tk.RIGHT, fill=Tk.Y)
            scrollbar.config(command=textbox.yview)
            textbox.config(bg='white', fg='black', insertbackground='black',
                yscrollcommand=scrollbar.set)
            for (name, style) in self.text_styles:
                textbox.tag_config(name, **style)
            for (key, command) in self.textbox_commands:
                textbox.bind(key, command)

    def change_fontsize(self, event):
        sign = 1 if event.delta > 0 else -1
        size = self.font.actual(option='size') + sign
        self.font.config(size=size)
        for textbox in self.textboxes:
            textbox.config(font=self.font)
            for (name, style) in self.text_styles:
                textbox.tag_config(name, **style)
        return 'break'

    def reset_fontsize(self, event):
        self.font.config(size=14)
        for textbox in self.textboxes:
            textbox.config(font=self.font)
            for (name, style) in self.text_styles:
                textbox.tag_config(name, **style)
        return 'break'

    @property
    def text_styles(self):
        strong = self.font.copy()
        strong.configure(weight='bold')
        em = self.font.copy()
        em.configure(slant='italic')
        underline = self.font.copy()
        underline.configure(underline=True, family='Calibri')
        small_caps = self.font.copy()
        size = small_caps.actual(option='size') - 3
        small_caps.configure(size=size, family='Algerian')
        highlulani = self.font.copy()
        size = highlulani.actual(option='size') + 3
        highlulani.configure(family='Lulani', size=size)
        return [
            ('strong', {'font': strong}),
            ('em', {'font': em}),
            ('small-caps', {'font': small_caps}),
            ('link', {'foreground': 'blue', 'font': underline}),
            ('high-lulani', {'font': highlulani})
        ]

    @property
    def textbox_commands(self):
        return [('<KeyPress>', self.master.edit_text_changed),
        ('<MouseWheel>', self.master.scroll_textbox),
        ('<Control-MouseWheel>', self.change_fontsize),
        ('<Control-a>', self.master.select_all),
        ('<Control-b>', self.master.bold),
        ('<Control-d>', self.add_heading),
        ('<Control-D>', self.remove_heading),
        ('<Control-e>', self.master.example_no_lines),
        ('<Control-f>', self.master.example),
        ('<Control-i>', self.master.italic),
        ('<Control-l>', self.master.load),
        ('<Control-k>', self.master.small_caps),
        ('<Control-K>', self.master.delete_line),
        ('<Control-m>', self.master.markdown_refresh),
        ('<Control-n>', self.master.add_link),
        ('<Control-N>', self.master.insert_new),
        ('<Control-o>', self.master.site_open),
        ('<Control-s>', self.master.save),
        ('<Control-t>', self.master.add_translation),
        ('<Control-0>', self.reset_fontsize),
        ('<Control-Up>', self.master.move_line_up),
        ('<Control-Down>', self.master.move_line_down),
        ('<Control-BackSpace>', self.master.backspace_word),
        ('<Control-Delete>', self.master.delete_word),
        ('<Alt-d>', self.master.go_to_heading),
        ('<Tab>', self.master.insert_spaces),
        ('<Shift-Tab>', self.master.previous_window)]

    def go_to(self, position):
        self.textboxes[0].mark_set(Tk.INSERT, position)
        self.textboxes[0].see(Tk.INSERT)

    def fill_headings(self, entries):
        while len(self.headings) < len(entries):
            self.add_heading()
        while len(self.headings) > len(entries):
            self.remove_heading()
        for heading, entry in zip(self.headings, entries):
            heading.delete(0, Tk.END)
            heading.insert(Tk.INSERT, entry)

    def add_heading(self, event=None):
        if len(self.headings) < 10:
            heading = Tk.Entry(self.headingframe)
            for (keys, command) in self.heading_commands:
                for key in keys:
                    heading.bind(key, command)
            heading.grid(column=0, columnspan=2, sticky=Tk.N)
            self.headings.append(heading)
        return 'break'

    def remove_heading(self, event=None):
        if len(self.headings) > 1:
            heading = self.headings.pop()
            heading.destroy()
        return 'break'

    def place_widgets(self):
        """
        Place all widgets in GUI window.
        Stack the textboxes on the right-hand side, taking as much
            room as possible.
        Stack the heading boxes, the buttons, radiobuttons and a
            label in the top-left corner.
        """
        self.master.top['menu'] = self.menu
        self.master.pack(expand=True, fill=Tk.BOTH)
        self.buttonframe.pack(side=Tk.LEFT)
        self.headingframe.grid(row=0, column=0, columnspan=2, sticky=Tk.N)
        self.textframe.pack(side=Tk.LEFT, expand=True, fill=Tk.BOTH)
        for heading in self.headings:
            heading.grid(column=0, columnspan=2, sticky=Tk.N)
        row = 1
        for i, button in enumerate(self.buttons):
            button.grid(row=row, column=i)
        row += 1
        for radio in self.radios:
            radio.grid(row=row, column=0, columnspan=2)
            row += 1
        for textbox in self.textboxes:
            textbox.pack(side=Tk.TOP, expand=True, fill=Tk.BOTH)
            row += 1
        self.info_label.grid(row=row, column=0, columnspan=2)
        self.blank_label.grid(row=row+1, column=0, columnspan=2)
