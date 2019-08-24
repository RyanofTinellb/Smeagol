from .site_editor import SiteEditor, Tk
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
        self.page = [entry]
        self.fill_and_load()
        return 'break'

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

    def update_titlebar(self):
        #override super().update_titlebar()
        try:
            name = self.entry.url
        except AttributeError:
            name = urlform(self.entry.get('name', ''))
        self._titlebar(buyCaps(name).replace('&nbsp;', ' '))

    def find_entry(self, headings, entry=None):
        # override super().find_entry()
        entry = self.site.root
        try:
            heading = un_url(headings[0])
        except IndexError:
            return entry
        initial = page_initial(headings[0]).capitalize()
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
        self.entry = self.find_entry(self.heading_contents)
        super(DictionaryEditor, self)._save_page()
        self.make_wordlist()

    @staticmethod
    @asynca
    def publish(entry=None, site=None, allpages=False):
        if allpages:
            site.publish()
        elif entry is not None:
            entry.update_date()
            entry.publish(site.template)
            entry.parent.sort()
            entry.parent.update_date()
            entry.parent.publish(site.template)
        if site is not None:
            site.update_source()
            site.update_searchindex()

    def update_tocs(self, new=False):
        # override super().update_tocs()
        if new:
            self.entry.root.sort()
            super(DictionaryEditor, self).update_tocs()

    def list_out(self, entry):
        # overrides super().list_out()
        lst = entry.list
        if len(lst) == 2:
            return lst[-1:]
        else:
            return None

    @asynca
    def make_wordlist(self):
        output = []
        transliteration = None
        language = None
        pos = None
        for entry in self.site.all_pages:
            transliteration = entry.name
            for line in self.remove_links(str(entry)).split('['):
                if line.startswith('1]'):
                    language = re.sub('1](.*?)\n(?:.*)', r'\1', line, flags=re.S)
                elif line.startswith('2]'):
                    pos = self._pos(line)
                elif line.startswith('d definition]'):
                    meaning, definition = self._meaning(line)
                    output.append(dict(
                        t=buyCaps(transliteration),
                        l=language,
                        p=pos,
                        d=definition,
                        m=meaning))
        dump(output, self.wordlist)

    def _pos(self, line):
        line = re.sub(r'2](.*?)\n+', r'\1', line)
        return [_f for _f in re.sub(r'\(.*?\)', '', line).split(' ') if _f]

    def _meaning(self, line):
        meaning = re.sub(r'd definition](.*?)\n+', r'\1', line)
        meaning = re.sub(r'</*.*?>|..:', '', meaning)
        definition = meaning.split(' ')
        return meaning, definition

    def initial_content(self, entry=None):
        if entry is None:
            entry = self.entry
        name = entry.get('name', '')
        tr = self.translator
        code = tr.code[:2]
        output = [
            f'[1]{tr.safename}',
            '[d native-script]',
            f'{tr.convert_word(name)}[/d]',
            f'[p {code}]<ipa>//</ipa>[/p]',
            '[2]',
            '[d definition]',
            '[/d]'
        ]
        if code == 'en':
            output.pop(1)
            output.pop(2)
        return self.markup('\n'.join(output))

    @property
    def textbox_commands(self):
        return super(DictionaryEditor, self).textbox_commands + [
            ('<Control-=>', self.add_definition),
            ('<Button-2>', self.set_jump_to_entry),
            ('<Control-Return>', self.jump_to_entry)
        ]


if __name__ == '__main__':
    DictionaryEditor().mainloop()
