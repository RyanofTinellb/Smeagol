import SimpleHTTPServer
import SocketServer
from socket import error as socket_error
import threading
import os
import random
import webbrowser as web
import Tkinter as Tk
from editor import Editor
from properties import Properties
from properties_window import PropertiesWindow
from text_window import TextWindow
from itertools import izip, izip_longest
from cwsmeagol.site.page import Page
from cwsmeagol.utils import *
from cwsmeagol.defaults import default


class SiteEditor(Editor, object):
    def __init__(self, master=None, config_file=None):
        super(SiteEditor, self).__init__(master)
        self.properties = Properties(config_file, self.caller)
        self.new_page = False
        self.server = None
        self.PORT = 41809
        self.start_server()
        self.fill_headings(self.page)
        self.load()
        self.go_to(self.position)

    @property
    def caller(self):
        return 'site'

    def setup_linguistics(self):
        self.languagevar = Tk.StringVar()
        self.languagevar.set(self.translator.fullname)

    def change_language(self, event=None):
        self.language = self.languagevar.get()
        for obj in (self.translator, self.randomwords):
            obj.select(self.language[:2])
        return 'break'

    def __getattr__(self, attr):
        if attr is 'properties':
            self.properties = Properties(self.caller)
            return self.properties
        try:
            return getattr(self.properties, attr)
        except AttributeError:
            return getattr(super(SiteEditor, self), attr)

    def __setattr__(self, attr, value):
        if attr is 'language':
            self.properties.language = value
        else:
            super(SiteEditor, self).__setattr__(attr, value)

    def set_frames(self):
        super(SiteEditor, self).set_frames()
        self.siteframe = Tk.Frame(self.sidebar)
        self.headingframe = Tk.Frame(self.siteframe)
        self.buttonframe = Tk.Frame(self.siteframe)
        self.master.title('Site Editor')
        self.master.protocol('WM_DELETE_WINDOW', self.quit)

    def ready(self):
        objs = ['headings', 'buttons']
        for obj in objs:
            getattr(self, 'ready_' + obj)()
        super(SiteEditor, self).ready()

    def ready_headings(self):
        master = self.headingframe
        self.headings = [Tk.Entry(master, width=25)]
        self.add_commands('Entry', self.heading_commands)

    def ready_buttons(self):
        master = self.buttonframe
        self.save_text = Tk.StringVar()
        self.save_text.set('Save')
        self.load_button = Tk.Button(master, text='Load',
                            command=self.load, width=10)
        self.save_button = Tk.Button(master, command=self.save_page,
                            textvariable=self.save_text, width=10)
        self.buttons = [self.load_button, self.save_button]

    def place_widgets(self):
        super(SiteEditor, self).place_widgets()
        self.siteframe.grid(row=0, column=0)
        self.headingframe.grid()
        self.buttonframe.grid()
        for i, heading in enumerate(self.headings):
            heading.grid(row=i, column=0)
        for i, button in enumerate(self.buttons):
            button.grid(row=0, column=i)

    def clear_interface(self):
        super(SiteEditor, self).clear_interface()
        for heading in self.headings:
            heading.delete(0, Tk.END)
        self.go_to_heading()

    @property
    def heading_contents(self):
        contents = [title.get() for title in self.headings if title]
        self.properties.heading_contents = contents
        return contents

    def fill_headings(self, entries):
        while len(self.headings) < len(entries):
            self.add_heading()
        while len(self.headings) > len(entries):
            self.remove_heading()
        for heading, entry in zip(self.headings, entries):
            self.replace(heading, entry)

    def go_to_heading(self, event=None):
        with ignored(IndexError):
            heading = self.headings[0]
            heading.focus_set()
            heading.select_range(0, Tk.END)
        return 'break'

    def scroll_headings(self, event):
        root = self.site.root
        heading = event.widget
        actual_level = self.headings.index(heading) + 2
        level = actual_level + root.level - 1
        direction = 1 if event.keysym == 'Next' else -1
        child = True
        # ascend hierarchy until correct level
        while self.entry.level > level:
            try:
                self.entry = self.entry.parent
            except AttributeError:
                break
        # traverse hierarchy sideways
        if self.entry.level == level:
            with ignored(IndexError):
                self.entry = self.entry.sister(direction)
        # descend hierarchy until correct level
        while self.entry.level < level:
            try:
                self.entry = self.entry.eldest_daughter
            except IndexError:
                child = False
                break
        for heading_ in self.headings[level - root.level - 1:]:
            heading_.delete(0, Tk.END)
        while len(self.headings) > actual_level:
            self.remove_heading()
        while child and len(self.headings) < min(actual_level, 10):
            self.add_heading()
        if child:
            heading.insert(Tk.INSERT, self.entry.name)
            self.master.title('Editing ' + self.entry.name)
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

    def enter_headings(self, event):
        headings = self.headings
        level = headings.index(event.widget)
        try:
            headings[level + 1].focus_set()
        except IndexError:
            self.load()
        return 'break'

    def previous_entry(self, event):
        self.load_entry(self.entry.previous)
        return 'break'

    def next_entry(self, event):
        self.load_entry(self.entry.next_node)
        return 'break'

    def load_entry(self, entry):
        ancestors = entry.ancestors[1:]
        actual_level = len(ancestors)
        while len(self.headings) > max(1, actual_level):
            self.remove_heading()
        while len(self.headings) < min(actual_level, 10):
            self.add_heading()
        for heading, ancestor in izip(self.headings, ancestors):
            heading.delete(0, Tk.END)
            heading.insert(0, ancestor.name)
        self.load()

    def site_open(self, event=None):
        source = self.open()
        self.languagevar.set(self.language)
        self.reset()
        return 'break'

    def start_server(self):
        handler = SimpleHTTPServer.SimpleHTTPRequestHandler
        while True:
            try:
                self.server = SocketServer.TCPServer(("", self.PORT), handler)
                name = self.site.name
                page404 = default.page404.format(
                    self.site[0].elder_links).replace(
                        '<li class="normal">{0}</li>'.format(name),
                        '<li><a href="/index.html">{0}</a></li>'.format(name)
                )
                page404 = re.sub(r'href="/*', 'href="/', page404)
                handler.error_message_format = page404
                break
            except socket_error:
                self.PORT += 1
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.start()

    def open_in_browser(self, event=None):
        web.open_new_tab(os.path.join('http://localhost:' +
                                      str(self.PORT), self.entry.link()))
        return 'break'

    def reset(self, event=None):
        self.entry = self.site.root
        self.clear_interface()
        self.fill_headings(self.page)
        self.load()

    def site_properties(self, event=None):
        properties_window = PropertiesWindow(self.properties)
        self.wait_window(properties_window)
        self.site.root.name = self.site.name
        self.save_site()

    def site_publish(self, event=None):
        self.information.set(self.site.publish())

    def load(self, event=None):
        self.entry = self.find_entry(self.heading_contents)
        text = self.prepare_entry(self.entry)
        self.display(text)
        self.reset_textbox()
        self.save_text.set('Save')
        try:
            self.master.title('Editing ' + self.entry.name)
        except AttributeError:
            self.master.title('Editing ' + self.entry.get('name', ''))
        return 'break'

    def find_entry(self, headings, entry=None):
        if entry is None:
            entry = self.site.root
        try:
            heading = headings.pop(0)
        except IndexError:
            return entry
        try:
            return self.find_entry(headings, entry[heading])
        except KeyError:
            self.new_page = True
            return dict(name=heading)

    def list_pages(self, event=None):
        def text_thing(page):
            return ' ' * 2 * page.level + page.name
        text = '\n'.join(map(text_thing, self.site))
        with conversion(self.markdown, 'to_markdown') as converter:
            text = converter(text)
        textwindow = TextWindow(text)
        self.wait_window(textwindow)
        return 'break'

    def prepare_entry(self, entry):
        try:
            text = self.initial_content(entry)
        except AttributeError:
            text = str(entry)
        for converter, function in ((self.linkadder, 'remove_links'),
                                    (self.markdown, 'to_markdown')):
            with conversion(converter, function) as converter:
                text = converter(text)
        return text

    def save_page(self, event=None):
        if self.is_new:
            self.site_properties()
        self.textbox.tag_remove(self.current_style.get(), Tk.INSERT)
        self.current_style.set('')
        self.tkinter_to_tkinter(self._save_page)
        self.save_text.set('Save')
        self.information.set('Saved!')
        self.save_site()
        return 'break'

    def _save_page(self):
        text = self.get_text(self.textbox)
        self.prepare_text(text)
        self.publish(self.entry, self.site)

    def save_wholepage(self):
        try:
            with open('wholetemplate.html') as template:
                template = template.read()
        except IOError:
            return False
        g = self.site
        self.errors = 0
        self.errorstring = ''
        k = '\n'.join(map(self._save_wholepage, g))
        page = template.replace('{toc}', g[0].family_links).replace(
            '{content}', k).replace(
            '{stylesheet}', g[0].stylesheet_and_icon).replace(
            '{copyright}', self.copyright)
        information = '{3}{0} error{2}\n{1}'.format(
                self.errors,
                '-' * 10,
                '' if self.errors == 1 else 's',
                self.errorstring
            )
        self.information.set(information)
        with open('wholepage.html', 'w') as p:
            p.write(page)
        return self.errors

    def _save_wholepage(self, page):
        try:
            return page.main_contents
        except ZeroDivisionError:
            self.errorstring += 'Error in ' + page.folder + '/' + page.name + '\n'
            self.errors += 1
            return ''

    @property
    def copyright(self):
        try:
            date = datetime.today()
        except ValueError:
            return ''
        suffix = "th" if 4 <= date.day <= 20 or 24 <= date.day <= 30 else [
            "st", "nd", "rd"][date.day % 10 - 1]
        output = datetime.strftime(
            date, '<span class="no-breaks">&copy;%Y Ryan Eakins.</span> <span class="no-breaks">Last updated: %A, %B %#d' + suffix + ', %Y.')
        return output

    @property
    def is_new(self):
        if self.site is None:
            return True
        elif not self.source:
            return True
        elif self.destination is None:
            return True
        return False

    @staticmethod
    def get_text(textbox):
        return str(textbox.get(1.0, Tk.END + '-1c'))

    def prepare_text(self, text):
        if self.entry.level and not text:
            if self.page == self.heading_contents:
                self.page = ['']
            self.entry.delete_htmlfile()
            self.entry.remove_from_hierarchy()
            self.reset()
        else:
            self.convert_text(text, self.entry)

    def convert_text(self, text, entry):
        text = re.sub(r'\n\n+', '\n', text)
        with conversion(self.markdown, 'to_markup') as converter:
            text = converter(text)
        with conversion(self.linkadder, 'add_links') as converter:
            text = converter(text, entry)
        self.entry.text = filter(None, text.split('['))

    @staticmethod
    def publish(entry, site, allpages=False):
        if allpages:
            site.publish()
        elif entry is not None:
            entry.publish(site.template)
        if site is not None:
            site.update_source()
            site.update_searchindex()

    @staticmethod
    def insert_characters(textbox, before, after=''):
        try:
            text = textbox.get(Tk.SEL_FIRST, Tk.SEL_LAST)
            textbox.delete(Tk.SEL_FIRST, Tk.SEL_LAST)
            textbox.insert(Tk.INSERT, before + text + after)
        except Tk.TclError:
            textbox.insert(Tk.INSERT, before + after)
            textbox.mark_set(Tk.INSERT, Tk.INSERT + '-{0}c'.format(len(after)))

    def insert_formatting(self, event, tag):
        with conversion(self.markdown, 'find_formatting') as converter:
            self.insert_characters(event.widget, *converter(tag))

    def insert_markdown(self, event, tag):
        with conversion(self.markdown, 'find') as converter:
            self.insert_characters(event.widget, converter(tag))

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

    def insert_new(self, event):
        self.entry.content = self.initial_content()
        self.load()
        return 'break'

    def select_paragraph(self, event=None):
        event.widget.tag_add('sel', Tk.INSERT + ' linestart',
                             Tk.INSERT + ' lineend +1c')
        return 'break'

    def quit(self):
        if self.save_wholepage():
            return
        self.server.shutdown()
        self.page = self.heading_contents
        self.language = self.languagevar.get()
        self.position = self.textbox.index(Tk.INSERT)
        self.fontsize = self.font.actual(option='size')
        self.save_site()
        self.master.quit()

    def initial_content(self, entry=None):
        if entry is None:
            entry = self.entry
        name = entry.get('name', '')
        return '1]{0}\n'.format(name)

    @property
    def textbox_commands(self):
        return super(SiteEditor, self).textbox_commands + [
            ('<Control-Prior>', self.previous_entry),
            ('<Control-Next>', self.next_entry),
            ('<Control-N>', self.insert_new),
            ('<Control-o>', self.site_open),
            ('<Control-s>', self.save_page)]

    @property
    def heading_commands(self):
        return [
            (('<Prior>', '<Next>'), self.scroll_headings),
            ('<Return>', self.enter_headings),
            ('<Control-M>', self.add_heading),
            ('<Control-N>', self.remove_heading)]

    @property
    def menu_commands(self):
        return [('Site', [('Open', self.site_open),
                ('Save', self.save_site),
                ('Save _As', self.save_site_as),
                ('Open in _Browser', self.open_in_browser),
                ('P_roperties', self.site_properties),
                ('S_ee All', self.list_pages),
                ('Publish _WholePage', self.save_wholepage),
                ('Publish All', self.site_publish)])
            ] + super(SiteEditor, self).menu_commands


if __name__ == '__main__':
    SiteEditor().mainloop()
