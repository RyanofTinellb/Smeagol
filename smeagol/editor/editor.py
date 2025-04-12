from smeagol.utilities import filesystem as fs
from smeagol.widgets.manager import Manager

# pylint: disable=R0904


class Editor(Manager):
    def __init__(self, filenames=None):
        super().__init__()
        if not filenames:
            filenames = [fs.open_smeagol()]
        self.tabs.open_sites(filenames)

    def open_site(self):
        root = fs.open_folder()
        filenames = fs.find_by_type(root, '.smg')
        self.tabs.open_sites(filenames, new_tab=True)

    def __getattr__(self, attr):
        match attr:
            case 'tab':
                value = self.tabs.current
            case 'textbox':
                value = self.tab.textbox
            case 'interface':
                value = self.tab.interface
            case 'entry':
                value = self.tab.entry
            case 'closed_tabs':
                value = self.tabs.closed
            case _default:
                try:
                    return super().__getattr__(attr)
                except AttributeError as e:
                    name = type(self).__name__
                    raise AttributeError(f"'{name}' object has no attribute '{attr}'") from e
        return value

    def __setattr__(self, attr, value):
        match attr:
            case 'title':
                self.parent.title(f'{value} - Sméagol Site Editor')
            case 'interface':
                self.tab.interface = value
            case 'entry':
                self.tab.entry = value
            case _default:
                super().__setattr__(attr, value)

    def open_entry_in_browser(self, _event=None):
        self.interface.open_entry_in_browser(self.entry)
        return 'break'

    def save_all_entries(self):
        self.tabs.save_all_entries()

    @property
    def menu_commands(self):
        return [
            ('File', [
                ('Open Site', self.open_site),
                ('Open in _Browser', self.open_entry_in_browser),
                ('Save All Entries', self.save_all_entries)]
            ),
            *super().menu_commands
        ]

    def quit(self):
        super().quit()
        self.tabs.save_all()
        print('Closing Servers...')
        fs.close_servers()
        print('Servers closed. Enjoy the rest of your day.')
