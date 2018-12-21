from site_editor import SiteEditor, Tk
from smeagol.site.page import Page
from smeagol.utils import *


class DictionaryEditor(SiteEditor):
    def __init__(self, master=None, config_file=None):
        super(DictionaryEditor, self).__init__(master, config_file)
        self.heading = self.headings[0]
        self.font.config(family='Courier New')

    def jump_to_entry(self, event):
        textbox = event.widget
        try:
            borders = (Tk.SEL_FIRST, Tk.SEL_LAST)
            entry = textbox.get(*borders)
        except Tk.TclError:
            entry = self.select_word(event)
        self.save_page()
        self.page = [entry]
        self.fill_and_load()

    def set_jump_to_entry(self, event):
        textbox = event.widget
        textbox.mark_set(Tk.INSERT, Tk.CURRENT)
        self.jump_to_entry(event)
        return 'break'

    @property
    def caller(self):
        return 'dictionary'

    def add_definition(self, event=None):
        widget = event.widget
        m = self.markdown.to_markdown
        self.insert_characters(
            widget, m('<div class="definition">'), m('</div>'))
        return 'break'

    def find_entry(self, headings, entry=None):
        # override super().find_entry()
        entry = self.site.root
        try:
            heading = headings[0]
        except IndexError:
            return entry
        initial = re.sub(r'.*?(\w).*', r'\1',
            urlform(heading)).capitalize()
        try:
            return entry[initial][heading]
        except KeyError:
            try:
                parent = entry[initial]
            except KeyError:
                parent = dict(name=initial, parent=entry, position='1.0')
            entry = dict(name=heading, parent=parent, position='1.0')
        return entry

    def _save_page(self):
        # override super()._save_page
        super(DictionaryEditor, self)._save_page()
        self.serialise()

    @staticmethod
    def publish(entry, site, allpages=False):
        if allpages:
            site.publish()
        elif entry is not None:
            entry.update_date()
            entry.parent.update_date()
            entry.publish(site.template)
            entry.parent.publish(site.template)
        if site is not None:
            site.update_source()
            site.update_searchindex()

    def update_tocs(self):
        # override super().update_tocs()
        pass

    def _quit(self):
        # override super()._quit()
        return False

    def remove_all_links(self, text):
        text = self.remove_links(text)
        return text[3:] if ':' in text else text

    def serialise(self):
        output = []
        transliteration = None
        language = None
        pos = None
        sieve = re.compile(r'3\](.*?) <div class="definition">(.*?)</div>')
        for entry in self.site:
            transliteration = entry.name
            for line in entry.text:
                if line.startswith('1]'):
                    language = re.sub('1](.*?)\n', r'\1', line)
                elif line.startswith('3]'):
                    line = sieve.sub(r'\1\n\2', self.remove_all_links(line))
                    try:
                        newpos, meaning = line.splitlines()
                    except:
                        continue
                    if newpos:
                        pos = re.sub(r'\(.*?\)', '', newpos).split(' ')
                    definition = re.split(r'\W*', re.sub(r'<.*?>', '', meaning))
                    output.append(dict(
                        t=buyCaps(transliteration),
                        l=language,
                        p=pos,
                        d=definition,
                        m=meaning))
        filename = ('c:/users/ryan/documents/tinellbianlanguages'
                        '/dictionary/wordlist.json')
        dump(output, filename)

    def initial_content(self, entry=None):
        if entry is None:
            entry = self.entry
        name = entry.get('name', '')
        tr = self.translator
        code = tr.code[:2]
        output = [
            '[1]{0}'.format(tr.safename),
            '[2]{0}'.format(tr.convert_word(name)),
            '[p {0}]//[/p]'.format(code),
            '[3] {{ }}'
        ]
        if code == 'en':
            output.pop(1)
        return self.markup('\n'.join(output))

    @property
    def textbox_commands(self):
        return super(DictionaryEditor, self).textbox_commands + [
            ('<Control-=>', self.add_definition),
            ('<Button-2>', self.set_jump_to_entry),
            ('<Control-Return>', self.jump_to_entry)
        ]


if __name__ == '__main__':
    links = [ExternalGrammar('c:/users/ryan/documents/'
                             'tinellbianlanguages/dictionarylinks.txt'),
             InternalDictionary()]
    app = DictionaryEditor(site=Dictionary(),
                           markdown=Markdown('c:/users/ryan/documents/'
                                             'tinellbianlanguages/dictionaryreplacements.mkd'),
                           links=AddRemoveLinks(links),
                           randomwords=RandomWords(20, 3))
    app.master.title('Dictionary Editor')
    app.mainloop()
