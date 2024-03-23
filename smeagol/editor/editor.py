import tkinter as tk
from tkinter import simpledialog as sd

from smeagol.utilities import filesystem as fs
from smeagol.utilities import utils
from smeagol.widgets import styles
from smeagol.widgets.manager import Manager
from smeagol.widgets.window import api as window


class Editor(Manager):
    def __init__(self, parent=None, filenames=None):
        super().__init__(parent)
        if filenames:
            self.open_sites(filenames)

    def open_sites(self, filenames=None):
        if filenames is None:
            filenames = [fs.open_smeagol()]
        self.tabs.open_sites(filenames)

    def open_site(self):
        self.tabs.open_site(fs.open_smeagol())

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
            case 'status':
                value = self.textbox.displays
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

    def change_language(self, _event=None):
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
        # pylint: disable=W0201
        self.entry = self._entry(event.widget.level)
        try:
            self.set_headings(self.entry.eldest_daughter)
            self.headings.select_last()
        except IndexError:
            self.textbox.focus_set()
            self.textbox.see(tk.INSERT)

    def open_entry_in_browser(self, _event=None):
        self.interface.open_entry_in_browser(self.entry)
        return 'break'

    # def open_entry(self, entry):
    #     self.set_headings(entry)
    #     self.entry = entry
    #     self.title = self.interface.site.root.name

    def reset_entry(self, _event=None):
        with utils.ignored(AttributeError):
            self.set_headings(self.entry)

    # def save_site(self, filename=''):
    #     try:
    #         self.interface.save()
    #     except IOError:
    #         self.save_site_as()

    # def save_site_as(self, filename=''):
    #     filename = filename or fs.save_smeagol()
    #     if filename:
    #         self.interface.filename = filename
    #         self.save_site()

    def set_headings(self, entry):
        self.headings.headings = [e.name for e in entry.lineage][1:]

    def rename_page(self, _event=None):
        name = self.entry.name
        name = sd.askstring(
            'Page Name', f'What is the new name of "{name}"?')
        if name:
            self.entry.name = name
            self.tab.name = name
            self.reset_entry()

    def save_page(self, _event=None):
        self.tabs.save_entry()
        return 'break'

    def refresh_random(self, _event=None):
        if r := self.interface.randomwords:
            self.status['randomwords'].set('\n'.join(r.words(15)))
        return 'break'

    def clear_random(self, _event=None):
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

    def markdown_clear(self, _event=None):
        text = self.interface.markdown.to_markup(self.textbox.text)
        self.textbox.replace(text)

    def markdown_apply(self, _event=None):
        text = self.interface.markdown.to_markdown(self.textbox.text)
        self.textbox.replace(text)

    def markdown_edit(self, _event=None):
        top = tk.Toplevel(self)
        editor = window.Markdown(top, self.interface.markdown)
        self.wait_window(top)
        self.interface.markdown = editor.markdown

    def template_edit(self, _event=None):
        top = tk.Toplevel(self)
        templates = self.interface.templates
        window.Templates(top, templates).grid()
        self.wait_window(top)

    def edit_styles(self, _event=None):
        top = tk.Toplevel()
        styles_window = styles.window.Window(top, self.interface.styles)
        styles_window.grid()
        top.protocol('WM_DELETE_WINDOW', styles_window.cancel)
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
        self.tabs.save_all()
        print('Closing Servers...')
        fs.close_servers()
        print('Servers closed. Enjoy the rest of your day.')
