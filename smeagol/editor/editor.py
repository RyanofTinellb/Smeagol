import tkinter as tk
from tkinter import simpledialog as sd

from ..utilities import errors
from ..utilities import filesystem as fs
from ..utilities import utils
from ..widgets.manager import Manager
from ..widgets import window
from smeagol.widgets import styles


class Editor(Manager):
    def __init__(self, parent=None, filenames=None):
        super().__init__(parent)
        if filenames:
            self.open_site(filenames)

    def open_site(self, event=None):
        filename = fs.open_smeagol()
        filenames = [filename]
        self.tabs.open_site(filenames)

    @property
    def interfaces(self):
        return self.tabs.interfaces

    def new_tab(self, event=None):
        self.tabs.new()
        return 'break'

    def reopen_tab(self, event=None):
        self.tabs.reopen()
        return 'break'

    def close_tab(self, event):
        self.tabs.close(event)
        return 'break'
    
    def change_tab(self, event):
        self.tabs.change()
        self.update_displays()
        self.change_language()
        self.set_headings(self.entry)
        return 'break'

    def __getattr__(self, attr):
        match attr:
            case 'tab':
                return self.tabs.current
            case 'textbox':
                return self.tab.textbox
            case 'entry':
                return self.tab.entry
            case 'status':
                return self.textbox.displays
            case 'closed_tabs':
                return self.tabs.closed
            case default:
                try:
                    return super().__getattr__(attr)
                except AttributeError:
                    raise errors.throw_error(AttributeError, self, attr)

    def __setattr__(self, attr, value):
        match attr:
            case 'title':
                self.parent.title(f'{value} - Sméagol Site Editor')
            case 'interface':
                self.tab.interface = value
            case 'entry':
                self.tab.entry = value
            case default:
                super().__setattr__(attr, value)

    def change_language(self, event=None):
        language = self.status['language'].get()
        self.interface.change_language(language)
        return 'break'

    def go_to(self, position):
        self.textbox.mark_set(tk.INSERT, position)
        self.textbox.see(tk.INSERT)

    def _entry(self, level):
        return self.interface.find_entry(self.headings.headings[:level+1])

    def previous_entry(self, event):
        entry = self._entry(event.widget.level)
        with utils.ignored(IndexError):
            self.set_headings(entry.previous_sister)
        return 'break'

    def next_entry(self, event):
        entry = self._entry(event.widget.level)
        try:
            entry = entry.next_sister
        except IndexError:
            with utils.ignored(IndexError):
                entry = entry.eldest_daughter
        self.set_headings(entry)
        return 'break'

    def load_entry(self, event):
        self.entry = self._entry(event.widget.level)
        try:
            self.set_headings(self.entry.eldest_daughter)
            self.headings.select_last()
        except IndexError:
            self.textbox.focus_set()
            self.textbox.see(tk.INSERT)

    def open_entry_in_browser(self, event=None):
        self.interface.open_entry_in_browser(self.entry)
        return 'break'

    def open_entry(self, entry):
        self.set_headings(entry)
        self.entry = entry
        self.title = self.interface.site.root.name

    def reset_entry(self, event=None):
        with utils.ignored(AttributeError):
            self.set_headings(self.entry)

    def save_site(self, filename=''):
        try:
            self.interface.save()
        except IOError:
            self.save_site_as()

    def save_site_as(self, filename=''):
        filename = filename or fs.save_smeagol()
        if filename:
            self.interface.filename = filename
            self.save_site()

    def set_headings(self, entry):
        self.headings.headings = [e.name for e in entry.lineage][1:]

    def rename_page(self, event=None):
        name = self.entry.name
        name = sd.askstring(
            'Page Name', f'What is the new name of "{name}"?')
        if name:
            self.entry.name = name
            self.tab.name = name
            self.reset_entry()

    def save_page(self, event=None):
        self.interface.save_page(self.textbox.formatted_text, self.entry)
        self.interface.save_site()
        return 'break'

    def refresh_random(self, event=None):
        if r := self.interface.randomwords:
            self.status['randomwords'].set('\n'.join(r.words(15)))
        return 'break'

    def clear_random(self, event=None):
        self.status['randomwords'].set('')
        return 'break'

    def replace(self, heading, text):
        heading.delete(*tk.ALL)
        heading.insert(tk.FIRST, text)

    def display(self, text):
        self.textbox.replace(str(text))
        self.textbox.focus_set()
        self.update_wordcount(self.textbox)
        self.hide_tags()

    def select_word(self, event):
        textbox = event.widget
        pattern = r'\n|[^a-zA-Z0-9_\'’-]'
        borders = (
            textbox.search(
                pattern, tk.INSERT, backwards=True, regexp=True
            ) + '+1c' or tk.INSERT + ' linestart',
            textbox.search(
                pattern, tk.INSERT, regexp=True
            ) or tk.INSERT + ' lineend'
        )
        textbox.tag_add(tk.SEL, *borders)
        return textbox.get(*borders)

    def markdown_clear(self, event=None):
        text = self.interface.markdown.to_markup(self.textbox.text)
        self.textbox.replace(text)

    def markdown_apply(self, event=None):
        text = self.interface.markdown.to_markdown(self.textbox.text)
        self.textbox.replace(text)

    def markdown_edit(self, event=None):
        top = tk.Toplevel(self)
        editor = window.MarkdownWindow(top, self.interface.markdown)
        self.wait_window(top)
        self.interface.markdown = editor.markdown

    def template_edit(self, event=None):
        top = tk.Toplevel(self)
        templates = self.interface.templates
        window.Templates(top, self.interface.templates).grid()
        self.wait_window(top)
        for template in templates.values():
            if template.edited:
                template.edited = False
                self.new_tab(interface=template)

    def edit_styles(self, event=None):
        top = tk.Toplevel()
        window = styles.Window(top, self.interface.styles)
        window.grid()
        top.protocol('WM_DELETE_WINDOW', window.cancel)
        top.title(f'{self.interface.site.name} Styles')
        self.wait_window(top)
        self.textbox.update_styles()
        self.interface.config['styles'] = dict(self.interface.styles.items())

    def show_window(self):
        self.set_window_size(self.top)
        self.parent.update()
        self.parent.deiconify()

    def quit(self):
        super().quit()
        self.interfaces.save_all()
        print('Closing Servers...')
        fs.close_servers()
        print('Servers closed. Enjoy the rest of your day.')

    @property
    def menu_commands(self):
        return [
            ('Site', [
                ('Open', self.open_site),
                ('Save', self.save_site),
                ('Save _As', self.save_site_as),
            ]),
            ('Page', [
                ('Rename', self.rename_page),
                ('Open in Browser', self.open_entry_in_browser),
            ]),
            ('Edit', [
                ('Styles', self.edit_styles),
                ('Markdown', self.markdown_edit),
                ('Templates', self.template_edit),
            ]),
        ]

    # @property
    def textbox_commands(self):
        return [
            ('<Control-r>', self.refresh_random),
            ('<Control-s>', self.save_page),
            ('<Control-t>', self.new_tab),
            ('<Control-T>', self.reopen_tab),
            ('<Control-w>', self.close_tab),
            ('<Enter>', self.reset_entry),
        ]

    @property
    def heading_commands(self):
        return [
            ('<Prior>', self.previous_entry),
            ('<Next>', self.next_entry),
            ('<Return>', self.load_entry),
        ]

    @property
    def language_commands(self):
        return [('<<ComboboxSelected>>', self.change_language)]

    @property
    def random_commands(self):
        return [
            ('<Button-1>', self.refresh_random),
            ('<Button-3>', self.clear_random),
        ]
