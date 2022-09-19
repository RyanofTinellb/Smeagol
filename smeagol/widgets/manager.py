import tkinter as tk
from tkinter import ttk
from smeagol.conversion import api as conversion
from smeagol.utilities import utils
from smeagol.widgets.api import HeadingFrame, Tabs


class Manager(tk.Frame):
    '''Manages widgets for Editor'''
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = self.master
        self.create_layout()
        self.parent.protocol('WM_DELETE_WINDOW', self.quit)
    
    def create_layout(self):
        top = self.winfo_toplevel()
        self.set_window_size(top)
        top['menu'] = self.menu()
        self.textframe().pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        self.sidebar.pack(side=tk.LEFT)
        self.pack()
    
    def set_window_size(self, top):
        top.state('normal')
        w = w_pos = int(top.winfo_screenwidth() / 2)
        h = top.winfo_screenheight() - 50
        h_pos = 0
        top.geometry(f'{w}x{h}+{w_pos}+{h_pos}')
    
    def menu(self):
        menubar = tk.Menu(self.parent)
        for submenu in self.menu_commands:
            self.add_submenu(menubar, submenu)
        return menubar

    def add_submenu(self, parent, menu):
        label, options = menu
        submenu = tk.Menu(parent, tearoff=0)
        parent.add_cascade(label=label, menu=submenu)
        for option in options:
            label, command = option
            underline = label.find('_')
            underline = 0 if underline == -1 else underline
            label = label.replace('_', '')
            keypress = label[underline]
            submenu.add_command(label=label, command=command,
                                underline=underline)
            submenu.bind(f'<KeyPress-{keypress}>', command)
    
    # @property
    def textframe(self):
        frame = tk.Frame(self.parent)
        options = dict(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.tabs = Tabs(frame, self.textbox_commands)
        self.tabs.pack(**options)
        return frame

    @property
    def sidebar(self):
        frame = tk.Frame(self.parent)
        self.headings = self.headings_frame(frame)
        self.headings.grid(row=0, column=0)
        self.displays = dict(
            wordcount=tk.Label(frame, font=('Arial', 14), width=20),
            style=tk.Label(frame, font=('Arial', 12)),
            language=self.language_display(frame),
            randomwords=self.random_words_display(frame))
        for row, display in enumerate(self.displays.values(), start=1):
            display.grid(row=row, column=0)
        tk.Label(frame, height=1000).grid(row=row+1, column=0)
        return frame
    
    def headings_frame(self, parent):
        frame = HeadingFrame(parent, bounds=(1, 10))
        frame.commands = self.heading_commands
        return frame
    
    def language_display(self, parent):
        translator = conversion.Translator()
        languages = [f'{code}: {lang().name}'
                     for code, lang in translator.languages.items()]
        menu = ttk.Combobox(parent,
                            values=languages,
                            height=2000,
                            width=25,
                            justify=tk.CENTER)
        menu.state(['readonly'])
        utils.bind_all(menu, self.language_commands)
        return menu
    
    def random_words_display(self, parent):
        label = tk.Label(parent, font=('Arial', 14))
        utils.bind_all(label, self.random_commands)
        return label
    
    def update_displays(self):
        for name, display in self.displays.items():
            display.config(textvariable=self.status[name])

    def quit(self):
        self.parent.withdraw()
        self.parent.quit()
    
    @property
    def menu_commands(self):
        return [
            ('Quit', [
                ('E_xit', self.quit)
            ])
        ]
    
    @property
    def tabs_commands(self):
        return []
    
    @property
    def heading_commands(self):
        return []
    
    @property
    def language_commands(self):
        return []

    @property
    def random_commands(self):
        return []