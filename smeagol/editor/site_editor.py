import os
import random
import SocketServer
import SimpleHTTPServer
import Tkinter as Tk
import webbrowser as web
import tkMessageBox as mb
import tkSimpleDialog as sd
from itertools import izip, izip_longest
from socket import error as socket_error
from editor import Editor
from properties import Properties
from properties_window import PropertiesWindow
from smeagol.utils import *
from smeagol.defaults import default


class SiteEditor(Properties, Editor):
    def __init__(self, master=None, config_file=None):
        super(SiteEditor, self).__init__(master=master,
                                         config=config_file,
                                         caller=self.caller)
        self.entry = dict(position='1.0')
        self.start_server(port=41809)
        self.fill_and_load()

    @property
    def caller(self):
        return 'site'

    def setup_linguistics(self):
        super(SiteEditor, self).setup_linguistics()
        self.languagevar = Tk.StringVar()
        self.languagevar.set(self.translator.fullname)

    def change_language(self, event=None):
        self.language = self.languagevar.get()
        for obj in (self.translator, self.randomwords):
            obj.select(self.language[:2])
        return 'break'

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
                            command=self.load_from_headings, width=10)
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
        get = lambda x: x.get()
        return filter(None, map(get, self.headings))

    def go_to_heading(self, event=None):
        with ignored(IndexError):
            heading = self.headings[0]
            heading.focus_set()
            heading.select_range(0, Tk.END)
        return 'break'

    def fill_and_load(self):
        self.fill_headings()
        self.load()

    def fill_headings(self):
        entries = self.page
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
        return 'break'

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
        if self.page <> self.heading_contents:
            self.history += self.heading_contents
        self.load()

    def load(self, event=None):
        try:
            self.entry.position = self.textbox.index(Tk.INSERT)
        except AttributeError:
            self.entry['position'] = self.textbox.index(Tk.INSERT)
        self.entry = self.find_entry(list(self.page))
        self.update_titlebar()
        text = self.prepare_entry(self.entry)
        self.display(text)
        self.reset_textbox()
        self.save_text.set('Save')
        try:
            self.go_to(self.entry.position)
        except AttributeError:
            self.go_to(self.entry['position'])
        return 'break'

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
        source = self.open_site()
        self.languagevar.set(self.language)
        self.reset()
        return 'break'

    def site_save(self):
        self.fontsize = self.font.actual(option='size')
        self.save_site()

    def site_properties(self, event=None):
        properties_window = PropertiesWindow(self)
        self.wait_window(properties_window)
        self.site.root.name = self.site.name
        self.save_site()

    @async
    def site_publish(self, event=None):
        self.site.publish()

    @async
    def start_server(self, port):
        self.PORT = port
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
        self.server.serve_forever()

    def open_in_browser(self, event=None):
        web.open_new_tab(os.path.join('http://127.0.0.1:' +
                                      str(self.PORT), self.entry.link))
        return 'break'

    def reset(self, event=None):
        self.entry = self.site.root
        self.clear_interface()
        self.fill_and_load()

    def update_titlebar(self):
        try:
            self._titlebar(self.entry.name)
        except AttributeError:
            self._titlebar(self.entry.get('name', ''))

    def _titlebar(self, name):
        self.master.title('Editing ' + name)

    def find_entry(self, headings, entry=None):
        if entry is None:
            entry = self.site.root
        try:
            heading = headings.pop(0)
        except IndexError:
            return entry
        if not isinstance(entry, dict):
            with ignored(KeyError):
                return self.find_entry(headings, entry[heading])
        child = dict(name=heading, parent=entry, position='1.0')
        return self.find_entry(headings, child)

    def list_pages(self, event=None):
        def text_thing(page):
            return ' ' * 10 * page.level + page.name
        text = '\n'.join(map(text_thing, self.site))
        text = self.markdown(text)
        self.show_file(text)

    def prepare_entry(self, entry):
        try:
            text = self.initial_content(entry) # entry is a dict
        except AttributeError:
            text = str(entry)
        for converter in (self.remove_links, self.markdown):
            text = converter(text)
        return text

    def prepare_text(self, text):
        text = re.sub(r'\n\n+', '\n', text)
        text = self.markup(text)
        text = self.add_links(text, self.entry)
        try:
            self.entry.text = text
        except AttributeError:
            self.entry['text'] = text

    def save_page(self, event=None):
        if self.is_new:
            self.site_properties()
        self.textbox.tag_remove(self.current_style.get(), Tk.INSERT)
        self.current_style.set('')
        self._save_page()
        self.save_text.set('Save')
        self.information.set('Saved!')
        self.save_site()
        return 'break'

    @tkinter()
    def _save_page(self):
        text = self.get_text(self.textbox)
        with ignored(AttributeError): # entry could be a dict
            parent = self.entry.pop('parent')
            self.entry, new_parent = self.chain_append(self.entry, parent)
            self.update_tocs(new_parent)
        self.prepare_text(text)
        self.publish(self.entry, self.site)

    def chain_append(self, child, parent, new_parent=False):
        try:
            return parent.append(child), new_parent
        except AttributeError: # parent is also a dict
            parent['children'] = [child]
            grandparent = parent.pop('parent')
            return self.chain_append(parent, grandparent, True)

    @async
    def update_tocs(self, new=None):
        # don't publish the whole site again if you're a dictionary,
        # unless the parent was also new.
        self.publish(site=self.site, allpages=True)

    @async
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
        page = re.sub('{(.*?): (.*?)}', g[0].section_replace,
            template.replace('{toc}', g[0].family_links).replace(
            '{main-contents}', k).replace(
            '{copyright}', self.copyright))
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
            return page.title_heading + page.main_contents + '<p></p>'
        except ZeroDivisionError:
            self.errorstring += 'Error in ' + page.folder + '/' + page.name + '\n'
            self.errors += 1
            return ''

    @async
    def save_search_page(self):
        for template in (
                ('searchtemplate.html', 'search.html'),
                ('404template.html', '404.html')):
            self._search(*template)

    def _search(self, template, filename):
        try:
            with open(template) as template:
                page = template.read()
        except IOError:
            return
        g = self.site.root
        page = re.sub('{(.*?): (.*?)}', g.section_replace, page)
        page = re.sub(
            r'<li class="normal">(.*?)</li>',
            r'<li><a href="index.html">\1</a></li>',
            page
        )
        if filename.startswith('404'):
            page = re.sub(r'href="/*', 'href="/', re.sub(
                r'src="/*', 'src="/', page))
        dumps(page, filename)

    @property
    def copyright(self):
        strftime = datetime.strftime
        copyright = '<div class="copyright">{0}</div>'
        date = datetime.today()
        if 4 <= date.day <= 20 or 24 <= date.day <= 30:
            suffix = 'th'
        else:
            suffix = ['st', 'nd', 'rd'][date.day % 10 - 1]
        span = '<span class="no-breaks">{0}</span>'
        templates = (('&copy;%Y '
                      '<a href="http://www.tinellb.com/about.html">'
                      'Ryan Eakins</a>.'),
                'Last updated: %A, %B %#d' + suffix + ', %Y.')
        spans = '\n'.join([span.format(strftime(date, template))
                            for template in templates])
        return copyright.format(spans)

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
        return textbox.get(1.0, Tk.END + '-1c').encode('ascii', 'replace')

    def delete_page(self, event=None):
        template = 'Are you sure you wish to delete {0}?'
        message = template.format(self.entry.name)
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
    @async
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
            text = textbox.get(Tk.SEL_FIRST, Tk.SEL_LAST)
            textbox.delete(Tk.SEL_FIRST, Tk.SEL_LAST)
            textbox.insert(Tk.INSERT, before + text + after)
        except Tk.TclError:
            textbox.insert(Tk.INSERT, before + after)
            textbox.mark_set(Tk.INSERT, Tk.INSERT + '-{0}c'.format(len(after)))

    def insert_formatting(self, event, tag):
        converter = self.marker.find_formatting
        self.insert_characters(event.widget, *converter(tag))

    def insert_markdown(self, event, tag):
        converter = self.marker.find
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

    def select_paragraph(self, event=None):
        event.widget.tag_add('sel', Tk.INSERT + ' linestart',
                             Tk.INSERT + ' lineend +1c')
        return 'break'

    def edit_script(self, event=None):
        default = 'Enter new JavaScript here'
        try:
            text = self.entry.script or default
        except AttributeError:
            text = self.entry.get('script', default)
        self.edit_file(text, self._edit_script)

    def _edit_script(self, script=None):
        try:
            if script:
                self.entry.script = script
            else:
                self.entry.remove_script()
        except AttributeError:
            if script:
                self.entry['script'] = script
            else:
                self.entry.pop('script', None)
        self.save_page()

    def edit_template(self, event=None):
        text = self.edit_file(text=self.template)
        self.refresh_template(new_template=text)
        message = 'Do you wish to apply this template to all pages?'
        if mb.askyesno('Delete', message):
            self.site_publish()
        self.textbox.focus_set()

    def edit_linkadder(self, adder):
        linkadder = self.linkadder
        text = self.edit_file(text=linkadder.string(adder))
        linkadder.refresh(text=text, adder=adder)
        message = 'Do you wish to apply these changes to all pages?'
        if mb.askyesno('Delete', message):
            self.update_pages()
        self.textbox.focus_set()

    @async
    def update_pages(self):
        for entry in self.site:
            old = str(entry)
            text = self.linkadder.remove_links(old)
            text = self.linkadder.add_links(text, entry)
            if old <> text:
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

    def edit_text_changed(self, event):
        value = super(SiteEditor, self).edit_text_changed(event)
        if event.widget.edit_modified():
            self.save_text.set('*Save')
        return value

    def quit(self):
        self.master.destroy()
        self.save_wholepage()
        self.save_search_page()
        with ignored(AttributeError):
            self.server.shutdown()
        self.save_site()
        self.master.quit()

    def initial_content(self, entry=None):
        # blank for sites, filled for dictionary entries
        if entry is None:
            entry = self.entry
        name = entry.get('name', '')
        return 'Describe {0} here!\n'.format(name)

    @property
    def textbox_commands(self):
        return super(SiteEditor, self).textbox_commands + [
            ('<Control-Prior>', self.previous_entry),
            ('<Control-Next>', self.next_entry),
            ('<Control-Shift-Prior>', self.earlier_entry),
            ('<Control-Shift-Next>', self.later_entry),
            ('<Alt-d>', self.go_to_heading),
            ('<Control-l>', self.load_from_headings),
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
                ('Template', self.edit_template)])
            ] + super(SiteEditor, self).menu_commands


if __name__ == '__main__':
    SiteEditor().mainloop()
