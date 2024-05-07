import tkinter as tk

from smeagol.widgets.api import Tabs
from smeagol.widgets.sidebar import Sidebar


class Manager(tk.Frame):
    '''Manages widgets for Editor'''

    def __init__(self, parent=None):
        self.tabs = None
        super().__init__(parent)
        self.parent = self.master
        self.styles_menu = tk.Menu(self.parent, tearoff=0)
        self.create_layout()
        self.parent.protocol('WM_DELETE_WINDOW', self.quit)

    def __getattr__(self, attr):
        match attr:
            case 'status':
                return self.textbox.displays
            case _default:
                try:
                    return super().__getattr__(attr)
                except AttributeError as e:
                    name = type(self).__name__
                    raise AttributeError(
                        f"'{name}' object has no attribute '{attr}'") from e

    def create_layout(self):
        top = self.winfo_toplevel()
        self.set_window_size(top)
        top['menu'] = self.menu
        self.sidebar = Sidebar(self).pack(side=tk.LEFT)
        self.textframe().pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        self.pack()

    def set_window_size(self, top):
        top.state('normal')
        w = w_pos = int(top.winfo_screenwidth() / 2)
        h = top.winfo_screenheight() - 100
        h_pos = 0
        top.geometry(f'{w}x{h}+{w_pos}+{h_pos}')

    @property
    def menu(self):
        menubar = tk.Menu(self.parent)
        menubar.add_cascade(label='Styles', menu=self.styles_menu)
        for submenu in self.menu_commands:
            self.add_submenu(menubar, submenu)
        return menubar

    def add_submenu(self, parent, menu):
        label, options = menu
        submenu = tk.Menu(parent, tearoff=0)
        parent.add_cascade(label=label, menu=submenu)
        for option in options:
            label, command = option
            underline = max(label.find('_'), 0)
            label = label.replace('_', '')
            keypress = label[underline]
            submenu.add_command(label=label, command=command,
                                underline=underline)
            submenu.bind(f'<KeyPress-{keypress}>', command)

    # @property
    def textframe(self):
        frame = tk.Frame(self.parent)
        options = {"side": tk.TOP, "expand": True, "fill": tk.BOTH}
        self.tabs = Tabs(frame, self.textbox_commands,
                         self.sidebar, self.parent.title)
        self.tabs.styles_menu = self.styles_menu
        self.tabs.pack(**options)
        return frame

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

    @property
    def textbox_commands(self):
        return []
