from .site_editor import SiteEditor, Tk
from smeagol.site.page import Page
from smeagol.utils import *
from ..widgets import Textbox


class DictionaryEditor(SiteEditor):
    def __init__(self, master=None, config_file=None):
        super().__init__(master, config_file)
        self.heading = self.headings[0]

    def jump_to_entry(self, event):
        textbox = event.widget
        try:
            entry = textbox.get(textbox.SELECTION)
        except Tk.TclError:
            entry = self.select_word(event)
        self.open_tab()
        self.page = [entry]
        self.fill_and_load()
        return 'break'

    def set_jump_to_entry(self, event):
        textbox = event.widget
        textbox.mark_set(Tk.INSERT, Tk.CURRENT)
        with ignored(Tk.TclError):
            textbox.tag_remove(Tk.SEL, *Tk.WHOLE_BOX)
        self.jump_to_entry(event)
        return 'break'

    @property
    def caller(self):
        return 'dictionary'

    def update_titlebar(self):
        # override SiteEditor
        try:
            name = self.entry.url
        except AttributeError:
            name = urlform(self.entry.get('name', ''))
        name = buyCaps(name).replace('&nbsp;', ' ')
        self._titlebar(name)
        self.rename_tab(name)

    def load_entry(self, headings, entry=None):
        # override SiteEditor
        entry = entry or self.site.root
        try:
            heading = un_url(headings[0])
        except IndexError:
            return entry
        initial = page_initial(heading).capitalize()
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
        super()._save_page()
        if not self.entry.is_root:
            self.entry = self.entry.parent.sort(self.entry)
        self.make_wordlist()
    
    def scroll_headings(self, event):
        # override SiteEditor
        return

    @staticmethod
    @asynca
    def publish(entry=None, site=None, allpages=False):
        if allpages:
            site.publish()
        elif entry is not None:
            entry.update_date()
            entry.publish(site.template)
            entry.parent.update_date()
            entry.parent.publish(site.template)
        if site is not None:
            site.update_source()
            site.update_searchindex()
    
    def new_textbox(self, master):
        # override SiteEditor
        textbox = Textbox(master, 'Courier New')
        self.add_commands(textbox, self.textbox_commands)
        return textbox

    def update_tocs(self, new=False):
        # override SiteEditor
        if new:
            self.entry = self.entry.root.sort(self.entry)
            super().update_tocs()

    def list_out(self, entry):
        # overrides SiteEditor
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
        for entry in self.site:
            transliteration = entry.name
            for line in self.remove_links(str(entry), entry).split('['):
                if line.startswith('1]'):
                    language = re.sub('1](.*?)\n(?:.*)',
                                      r'\1', line, flags=re.S)
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

    @property
    def initial_content(self):
        name = self.entry.get('name', '')
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
            output.pop(1)
        return self.markup('\n'.join(output))

    @property
    def textbox_commands(self):
        return super().textbox_commands + [
            ('<Button-2>', self.set_jump_to_entry),
            ('<Control-Return>', self.jump_to_entry)
        ]


if __name__ == '__main__':
    DictionaryEditor().mainloop()
