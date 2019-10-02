from http.server import SimpleHTTPRequestHandler as HTTPHandler
import os
import socket
import socketserver
import tkinter.messagebox as mb
import tkinter.simpledialog as sd
import webbrowser as web
from itertools import zip_longest

from ..defaults import default

from .editor import *
from .interface import Interface


class SiteEditor(Interface, Editor):
    def __init__(self, master=None, config_file=None, tests=None):
        super().__init__(master=master,
                         config=config_file,
                         caller=self.caller)
        self.entry = dict(position='1.0')
        self.start_server(port=41809)
        self.fill_and_load()
        if tests:
            tests(self)

    def __getattr__(self, attr):
        if attr in {'textbox', 'entry'}:
            return getattr(self.current_tab, attr)
        elif attr in {'font'}:
            return getattr(self.textbox, attr)
        elif attr.startswith('entry_'):
            obj, attr = attr.split('_', 1)
            try:
                return getattr(self.entry, attr)
            except AttributeError:  # entry is a dict
                return self.entry.get(attr, '')
        else:
            return super().__getattr__(attr)

    def __setattr__(self, attr, value):
        if attr.startswith('entry_'):
            obj, attr = attr.split('_')
            try:
                setattr(self.entry, attr, value)
            except AttributeError:
                if value:
                    self.entry[attr] = value
                else:
                    self.entry.pop(attr, '')
        elif attr in {'textbox', 'entry'}:
            setattr(self.current_tab, attr, value)
        else:
            super().__setattr__(attr, value)

    @property
    def caller(self):
        return 'site'

    @property
    def current_tab(self):
        return self.notebook.nametowidget(self.notebook.select())

    def setup_linguistics(self):
        super().setup_linguistics()
        self.languagevar = Tk.StringVar()
        self.languagevar.set(self.translator.fullname)

    def change_language(self, event=None):
        self.language = self.languagevar.get()
        self.randomwords.sample_texts = self.sample_texts
        for obj in (self.translator, self.randomwords):
            obj.select(self.language[:2])
        return 'break'

    def ready_frames(self):
        super().ready_frames()
        self.siteframe = Tk.Frame(self.sidebar)
        self.headingframe = Tk.Frame(self.siteframe)
        self.buttonframe = Tk.Frame(self.siteframe)
        self.master.title('Site Editor')
        self.master.protocol('WM_DELETE_WINDOW', self.quit)

    def ready_headings(self):
        master = self.headingframe
        self.headings = [Tk.Entry(master, width=25)]
        self.add_commands('Entry', self.heading_commands)

    def ready_buttons(self):
        master = self.buttonframe
        self.save_text = Tk.StringVar()
        self.save_text.set('Save')
        self.load_button = Tk.Button(master, text='Load',
                                     command=self.load_from_headings, width=10)
        self.save_button = Tk.Button(master, command=self.save,
                                     textvariable=self.save_text, width=10)
        self.buttons = [self.load_button, self.save_button]

    def ready_textbox(self):
        self.ready_notebook()

    def new_textbox(self, master):
        textbox = Textbox(master)
        self.add_commands(textbox, self.textbox_commands)
        return textbox

    def ready_notebook(self):
        self.closed_tabs = []
        self.notebook = ttk.Notebook(self.textframe)
        self.notebook.bind('<<NotebookTabChanged>>', self.change_tab)
        self.notebook.bind('<Button-2>', self.close_tab)
        self.notebook.pack(side=Tk.TOP, expand=True, fill=Tk.BOTH)
        self.open_tab()

    def place_widgets(self):
        super().place_widgets()
        self.siteframe.grid(row=0, column=0)
        self.headingframe.grid()
        self.buttonframe.grid()
        for i, heading in enumerate(self.headings):
            heading.grid(row=i, column=0)
        for i, button in enumerate(self.buttons):
            button.grid(row=0, column=i)

    def open_tab(self, event=None):
        frame = Tk.Frame(self.notebook)
        textbox = self.new_textbox(frame)
        textbox.pack(side=Tk.LEFT, expand=True, fill=Tk.BOTH)
        frame.textbox = textbox
        self.notebook.add(frame)
        self.notebook.select(frame)
        self.entry = dict(position='1.0')
        with ignored(AttributeError):
            self.go_to_heading()
        return 'break'

    def change_tab(self, event=None):
        frame = self.current_tab
        with ignored(AttributeError):
            self.entry = frame.entry
            self.fill_headings(frame.page)
            self.update_titlebar()

    def close_tab(self, event=None):
        if self.notebook.index('end') - len(self.closed_tabs) > 1:
            tab = f'@{event.x},{event.y}'
            while True:
                try:
                    self.notebook.hide(tab)
                    self.closed_tabs += [tab]
                    break
                except Tk.TclError:
                    tab = self.notebook.select()
        return 'break'

    def reopen_tab(self, event=None):
        with ignored(IndexError):
            tab = self.closed_tabs.pop()
            self.notebook.add(tab)
            self.notebook.select(tab)
        return 'break'

    def rename_tab(self, text):
        self.notebook.tab(self.current_tab, text=text)

    @property
    def heading_contents(self):
        def get(x): return x.get()
        return [_f for _f in map(get, self.headings) if _f]

    def go_to_heading(self, event=None):
        with ignored(IndexError):
            heading = self.headings[0]
            heading.focus_set()
            heading.select_range(*Tk.ALL)
        return 'break'

    def fill_and_load(self):
        self.fill_headings()
        self.load()

    def fill_headings(self, entries=None):
        entries = entries or self.page
        if len(entries):
            while len(self.headings) < len(entries) < 10:
                self.add_heading()
            while len(self.headings) > len(entries) > 0:
                self.remove_heading()
            for heading, entry in zip(self.headings, entries):
                self.replace(heading, entry)
        else:
            while len(self.headings) > 1:
                self.remove_heading()
            self.replace(self.headings[0], '')

    def scroll_headings(self, event):
        if (event.char == '' and event.keysym not in ('Prior', 'Next')
                or event.keysym in ('Return',)
                or isinstance(self.h_entry, dict)):
            return
        heading = event.widget
        actual_level = self.headings.index(heading) + 2
        level = actual_level - 1
        direction = dict(Next=1, Prior=-1).get(event.keysym, 0)
        self.h_entry = self.h_entry or self.entry.new()
        child = True
        # ascend hierarchy until correct level
        while self.h_entry.level > level:
            try:
                self.h_entry = self.h_entry.parent
            except AttributeError:
                break
        # traverse hierarchy sideways
        if self.h_entry.level == level:
            if direction:
                with ignored(IndexError):
                    self.h_entry = self.h_entry.sister(direction)
            else:
                text = heading.get()[:heading.index(Tk.INSERT)].lower()
                if text:
                    sisters = [s for s in self.h_entry.sisters
                               if s.name.lower().startswith(text)]
                    self.h_entry = sisters[0] if sisters else None
        # descend hierarchy until correct level
        while self.h_entry and self.h_entry.level < level:
            try:
                self.h_entry = self.h_entry.eldest_daughter
            except IndexError:
                child = False
                break
        for heading_ in self.headings[level - 1:]:
            if self.h_entry:
                heading_.delete(*Tk.ALL)
        while len(self.headings) > actual_level:
            self.remove_heading()
        while child and len(self.headings) < min(actual_level, 10):
            self.add_heading()
        if child and self.h_entry:
            heading.insert(Tk.INSERT, self.h_entry.name)

    def clear_h_entry(self, event=None):
        self.h_entry = self.load_entry(self.heading_contents)

    def enter_headings(self, event):
        headings = self.headings
        try:
            level = headings.index(event.widget) + 1
        except ValueError:
            level = 0
        try:
            headings[level].focus_set()
        except IndexError:
            self.load_from_headings()
        return 'break'

    def load_from_headings(self, event=None):
        if self.page != self.heading_contents:
            self.history += self.heading_contents
        self.load()

    def load(self, event=None):
        self.entry_position = self.textbox.index(Tk.INSERT)
        self.entry = self.load_entry(list(self.page))
        self.current_tab.page = list(self.page)
        self.current_tab.entry = self.entry
        self.initial_text = self.formatted_entry
        self.update_titlebar()
        self.display(self.initial_text)
        self.textbox.reset()
        self.save_text.set('Save')
        self.go_to(self.entry_position)
        return 'break'

    @property
    def formatted_entry(self):
        text = self._entry
        if isinstance(text, list):
            text = '['.join(text)
        return self.Text(text).remove_links.markdown

    @property
    def _entry(self):
        try:
            return self.initial_content  # entry is a dict
        except AttributeError:
            return str(self.entry)

    def earlier_entry(self, event=None):
        self.history.previous()
        self.fill_and_load()
        return 'break'

    def later_entry(self, event=None):
        self.history.next()
        self.fill_and_load()
        return 'break'

    def list_out(self, entry):
        return entry.list

    def previous_entry(self, event=None):
        try:
            entry = self.entry.predecessor
        except IndexError:
            entry = self.entry.youngest_granddaughter
        except AttributeError:
            return 'break'
        entry = self.list_out(entry)
        if entry is not None:
            self.history += entry
            self.fill_and_load()
        return 'break'

    def next_entry(self, event=None):
        try:
            entry = self.entry.successor
        except IndexError:
            entry = self.entry.root
        except AttributeError:
            return 'break'
        entry = self.list_out(entry)
        if entry is not None:
            self.history += entry
            self.fill_and_load()
        return 'break'

    def add_heading(self, event=None):
        if len(self.headings) < 10:
            heading = Tk.Entry(self.headingframe, width=25)
            heading.grid(column=0, columnspan=2, sticky=Tk.N)
            self.headings.append(heading)
        return 'break'

    def remove_heading(self, event=None):
        if len(self.headings) > 1:
            heading = self.headings.pop()
            heading.destroy()
        return 'break'

    def site_open(self, event=None):
        self.open_site()
        self.languagevar.set(self.language)
        self.reset()
        return 'break'

    @asynca
    def site_publish(self, event=None):
        for page in self.site:
            page.text = self.add_links(
                self.remove_links(str(page), page), page)
        self.site.publish()
        print('Site Published!')

    @asynca
    def start_server(self, port):
        self.PORT = port
        while True:
            try:
                self.server = socketserver.TCPServer(
                    ("", self.PORT), HTTPHandler)
                name = self.site.name
                page404 = default.page404.format(
                    self.site[0].elder_links).replace(
                        f'<li class="normal">{name}</li>',
                        f'<li><a href="/index.html">{name}</a></li>'
                )
                page404 = re.sub(r'href="/*', 'href="/', page404)
                HTTPHandler.error_message_format = page404
                break
            except socket.error:
                self.PORT += 1
        self.server.serve_forever()

    def open_in_browser(self, event=None):
        web.open_new_tab(os.path.join('http://127.0.0.1:' +
                                      str(self.PORT), self.entry.link))
        return 'break'

    def update_titlebar(self):
        self._titlebar(self.entry_name)
        self.rename_tab(self.entry_name)

    def _titlebar(self, name):
        self.master.title('Editing ' + name)

    def load_entry(self, headings, entry=None):
        if entry is None:
            entry = self.site.root
        if headings:
            heading = headings.pop(0)
            if isinstance(entry, dict):
                child = dict(name=heading, parent=entry, position='1.0')
                return self.load_entry(headings, child)
            else:
                try:
                    return self.load_entry(headings, entry[heading])
                except KeyError:
                    child = dict(name=heading, parent=entry, position='1.0')
                    return self.load_entry(headings, child)
        else:
            return entry

    def list_pages(self, event=None):
        def text_thing(page):
            return ' ' * 10 * page.level + page.name
        text = '\n'.join(map(text_thing, self.site))
        text = self.markdown(text)
        self.show_file(text)

    def save(self, event=None):
        if self.is_new():
            self.site_properties()
        self.clear_style()
        self.save_text.set('Save')
        self._save_page()
        self.publish(self.entry, self.site)
        self._save_site()
        return 'break'

    def clear_style(self):
        self.textbox.tag_remove(self.current_style.get(), Tk.INSERT)
        self.current_style.set('')

    def _save_page(self):
        with ignored(AttributeError):  # entry could be a dict
            parent = self.entry.pop('parent')
            self.entry, new_parent = self.chain_append(self.entry, parent)
            self.update_tocs(new_parent)
        self.entry_text = str(self.Text(self.textbox).markup.add_links)

    def chain_append(self, child, parent, new_parent=False):
        try:
            return parent.append(child), new_parent
        except AttributeError:  # parent is also a dict
            parent['children'] = [child]
            grandparent = parent.pop('parent')
            return self.chain_append(parent, grandparent, True)

    @asynca
    def update_tocs(self, new=None):
        # don't publish the whole site again if you're a dictionary,
        # unless the parent was also new.
        self.publish(site=self.site, allpages=True)

    def _save_site(self):
        self.fontsize = self.font.actual(option='size')
        self.save_site()
        self.save_wholepage()
        self.save_search_pages()

    # @property
    def is_new(self):
        if self.site is None:
            return True
        elif not self.source:
            return True
        elif self.destination is None:
            return True
        return False

    def delete_page(self, event=None):
        message = f'Are you sure you wish to delete {self.entry.name}?'
        if mb.askokcancel('Delete', message):
            self.entry.delete()
            self.page.pop()
            self.reset()
        return 'break'

    def rename_page(self):
        new_name = sd.askstring('Rename', 'What is the new name?',
                                initialvalue=self.entry.name)
        if new_name:
            try:
                self.entry.delete_html()
                self.entry.name = new_name
                self.entry.refresh_flatname()
            except AttributeError:
                self.entry['name'] = new_name
            with ignored(IndexError):
                self.page[-1] = new_name
            self.update_titlebar()
            self.fill_headings()

    @staticmethod
    @asynca
    def publish(entry=None, site=None, allpages=False):
        if allpages:
            site.publish()
        elif entry is not None:
            entry.update_date()
            entry.publish(site.template)
        if site is not None:
            site.update_source()
            site.update_searchindex()

    @staticmethod
    def insert_characters(textbox, before, after=''):
        try:
            text = textbox.getTk.SELECTION
            textbox.deleteTk.SELECTION
            textbox.insert(Tk.INSERT, before + text + after)
        except Tk.TclError:
            textbox.insert(Tk.INSERT, before + after)
            textbox.mark_set(Tk.INSERT, Tk.INSERT + f'-{len(after)}c')

    def format_paragraph(self, style, code, textbox):
        linestart = Tk.INSERT + ' linestart'
        text = textbox.get(linestart, linestart + '+2c')
        self.remove_paragraph_formatting(textbox)
        if text == code or text == '[' + code[0]:
            return
        textbox.insert(linestart, code)
        textbox.tag_add(style, linestart, linestart + '+2c')

    def remove_paragraph_formatting(self, textbox):
        linestart = Tk.INSERT + ' linestart'
        text = textbox.get(linestart, linestart + '+2c')
        if text in ('e ', 'f '):
            textbox.delete(linestart, linestart + '+2c')
        elif text in ('[e', '[f'):
            textbox.delete(linestart, linestart + '+3c')

    def select_paragraph(self, event=None):
        event.widget.tag_add(Tk.SEL, *Tk.CURRLINE)
        return 'break'

    def edit_script(self, event=None):
        default = 'Enter new JavaScript here'
        text = self.entry_script or default
        self.edit_file(text, self._edit_script)

    def _edit_script(self, script=None):
        '''
        Called once the script edit screen is closed
        '''
        self.entry_script = script
        self.save()

    def edit_linkadder(self, adder):
        linkadder = self.linkadder
        text = self.edit_file(text=linkadder.string(adder))
        linkadder.refresh(text=text, adder=adder)
        message = 'Do you wish to apply these changes to all pages?'
        if mb.askyesno('Delete', message):
            self.update_pages()
        self.textbox.focus_set()

    @asynca
    def update_pages(self):
        for entry in self.site:
            old = str(entry)
            text = self.linkadder.remove_links(old)
            text = self.linkadder.add_links(text, entry)
            if old != text:
                entry.text = text
                entry.publish(self.site.template)
        self.site.update_source()

    def refresh_broken_links(self):
        for linker in ('ExternalDictionary', 'InternalDictionary'):
            with ignored(KeyError):
                self.linkadder.refresh('', linker)

    def edit_external_grammar(self):
        self.edit_linkadder('ExternalGrammar')

    def edit_glossary(self):
        self.edit_linkadder('Glossary')

    def key_released(self, event):
        # overrides Editor
        super().key_released(event)
        if event.widget.edit_modified():
            self.save_text.set('*Save')
    
    def reset(self, event=None):
        self.entry = self.site.root
        self.clear_interface()
        self.fill_and_load()

    def clear_interface(self, event=None):
        super().clear_interface()
        # self.display(self.initial_text)
        # self.information.set('')
        self.save_text.set('Save')

    def cancel_changes(self, event=None):
        # override Editor
        self.clear_interface()

    def quit(self):
        self.master.destroy()
        with ignored(AttributeError):
            self.server.shutdown()
        self.master.quit()

    @property
    def initial_content(self):
        # blank for sites, filled for dictionary entries
        name = self.entry.get('name', '')
        return f'Describe {name} here!\n'
    
    @property
    def widgets(self):
        return super().widgets + ['headings', 'buttons']

    @property
    def textbox_commands(self):
        return super().textbox_commands + [
            ('<Control-Prior>', self.previous_entry),
            ('<Control-Next>', self.next_entry),
            ('<Control-Shift-Prior>', self.earlier_entry),
            ('<Control-Shift-Next>', self.later_entry),
            ('<Alt-d>', self.go_to_heading),
            ('<Control-l>', self.load_from_headings),
            ('<Control-o>', self.site_open),
            ('<Control-s>', self.save),
            ('<Control-t>', self.open_tab),
            ('<Control-T>', self.reopen_tab),
            ('<Control-w>', self.close_tab)]

    @property
    def heading_commands(self):
        return [
            ('<KeyRelease>', self.scroll_headings),
            ('<FocusIn>', self.clear_h_entry),
            ('<Return>', self.enter_headings),
            ('<Control-M>', self.add_heading),
            ('<Control-N>', self.remove_heading),
            ('<Control-t>', self.open_tab),
            ('<Control-T>', self.reopen_tab),
            ('<Control-w>', self.close_tab)]

    @property
    def menu_commands(self):
        return [('Site', [('Open', self.site_open),
                          ('Save', self.save_site),
                          ('Save _As', self.save_site_as),
                          ('P_roperties', self.site_properties),
                          ('S_ee All', self.list_pages),
                          ('Publish _WholePage', self.save_wholepage),
                          ('Publish All', self.site_publish)]),
                ('Page', [('Rename', self.rename_page),
                          ('Delete', self.delete_page),
                          ('Open in _Browser', self.open_in_browser)]),
                ('Links', [('Edit _External Grammar Links', self.edit_external_grammar),
                           ('Edit _Glossary', self.edit_glossary),
                           ('Refresh Broken Links', self.refresh_broken_links)]),
                ('Edit', [('Script', self.edit_script),
                          ('Templates', self.edit_templates)])
                ] + super().menu_commands


if __name__ == '__main__':
    SiteEditor().mainloop()
