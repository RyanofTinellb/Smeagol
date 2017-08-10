from editor import *


class DictionaryEditor(Editor):
    def __init__(self, directory, datafile, site, markdown, replacelinks, randomwords, master=None):
        """
        :param directory (String): the path and filename of the top-level directory
        :param datafile (String): the path, filename and extension of the data file, relative to directory
        :param site (Site): the site being modified
        :param markdown (String): the path, filename and extension of the replacements file, relative to directory
        :param randomwords (int): the number of random words to appear when requested
        """
        self.font = ('Courier New', '15')
        widgets = WidgetAmounts(headings=1, textboxes=1, radios='languages')
        super(DictionaryEditor, self).__init__(directory, datafile, site, markdown, replacelinks, widgets=widgets)

        # rename for readability
        self.heading = self.headings[0]
        self.edit_text = self.textboxes[0]
        self.markdown = self.markdowns
        self.site = self.sites
        self.datafile = self.datafiles
        self.words = randomwords.words

        self.configure_widgets()

        # initialise instance variables
        self.entry, self.entries, self.current, self.page = '', [], -1, None

    def configure_widgets(self):
        self.configure_language_radios()
        self.heading.bind('<Control-r>', self.refresh_random)
        self.heading.bind('<Prior>', self.scroll_headings)
        self.heading.bind('<Next>', self.scroll_headings)
        self.heading.bind('<Return>', self.load)
        self.edit_text.bind('<Control-r>', self.refresh_random)
        self.edit_text.bind('<Control-t>', self.add_translation)
        self.edit_text.bind('<Control-=>', self.add_definition)
        self.edit_text.bind('<Prior>', self.scroll_history)
        self.edit_text.bind('<Next>', self.scroll_history)

    def initial_content(self):
        """
        Insert the appropriate template for a new entry, and move the insertion pointer to allow for immediate input of the pronunciation.
        :precondition: The name of the entry, and its language, are already selected.
        """
        name = self.heading.get()
        trans = self.translator
        before = ('2]{0}\n[3]{1}\n').format(name, trans.name)
        before += '' if self.language.get() == 'en' else '[4]{0}\n'.format(trans.convert_word(name))
        before += '[5][p {0}]/'.format(trans.code)
        after = '/[/p]\n[6]\n'
        self.insert_characters(self.textboxes[0], before, after)
        self.textboxes[0].focus_set()

    def add_definition(self, event=None):
        """
        Insert the markdown for entry definition, and move the insertion pointer to allow for immediate input of the definition.
        """
        self.insert_characters(event, *self.markdown.find_formatting('div'))
        self.insert_characters(event, ' ' + self.markdown.find('class="definition">'))
        return 'break'

    def refresh_random(self, event=None):
        """
        Show a certain number of random nonsense words using High Lulani phonotactics.
        """
        self.information.set('\n'.join(self.words()))
        return 'break'

    def scroll_headings(self, event):
        if event.keysym == 'Prior':
            if self.current > 0:
                self.current -= 1
                self.heading.delete(0, Tk.END)
                self.heading.insert(0, self.markdown.to_markdown(self.entries[self.current]))
        elif event.keysym == 'Next':
            if self.current < len(self.entries) - 1:
                self.current += 1
                self.heading.delete(0, Tk.END)
                self.heading.insert(0, self.markdown.to_markdown(self.entries[self.current]))
        return 'break'

    def scroll_history(self, event):
        self.scroll_headings(event)
        self.load()
        return 'break'

    def add_translation(self, event=None):
        """
        Insert a transliteration of the selected text in the current language.
        Do sentence conversion if there is a period in the text, and word conversion otherwise.
        Insert an additional linebreak if the selection ends with a linebreak.
        """
        try:
            text = self.edit_text.get(Tk.SEL_FIRST, Tk.SEL_LAST)
        except Tk.TclError:
            text = self.edit_text.get(Tk.INSERT + ' wordstart', Tk.INSERT + ' wordend')
        converter = self.translator.convert_sentence if '.' in text else self.translator.convert_word
        text = converter(text)
        try:
            text += '\n' if self.edit_text.compare(Tk.SEL_LAST, '==', Tk.SEL_LAST + ' lineend') else ' '
            self.edit_text.insert(Tk.SEL_LAST + '+1c', text)
        except Tk.TclError:
            text += ' '
            self.edit_text.mark_set(Tk.INSERT, Tk.INSERT + ' wordend')
            self.edit_text.insert(Tk.INSERT + '+1c', text)
        self.edit_text.mark_set(Tk.INSERT, '{0}+{1}c'.format(Tk.INSERT, str(len(text) + 1)))
        return 'break'

    @staticmethod
    def prepare_entry(entry, markdown=None, kind=None):
        """
        Manipulate entry content to suit textboxes.
        Subroutine of self.load()
        Overrides method in Editor.py.
        :param entry (Page): A Page instance carrying text. Other Pages relative to this entry may also be accessed.
        :param markdown (Markdown): a Markdown instance to be applied to the contents of the entry. If None, the content is not changed.
        :param return (str[]):
        """
        content = entry.content # for code maintenance: so that next steps can be permuted easily.
        content = re.sub(r'<a href=\"(?!http).*?\">(.*?)</a>', r'<link>\1</link>', content)
        # protect phonology links from subsequent line
        content = re.sub(r'<a( href=\"http://grammar.*?phonology.*?</a>)', r'<b\1', content)
        content = re.sub(r'<a href=\"http://grammar.*?\">(.*?)</a>', r'\1', content)
        # un-protect phonology
        content = re.sub(r'<b( href=\"http://grammar.*?phonology.*?</a>)', r'<a\1', content)
        with conversion(markdown, 'to_markdown') as converter:
            content = converter(content)
        return [content]

    def find_entry(self, headings):
        """
        Find the current entry based on what is in the heading boxes.
        Overrides Editor.find_entry.
        Subroutine of self.load().
        :param headings (str[]): the texts from the heading boxes
        :return (Page):
        """
        heading = headings[0]
        site = self.sites
        with conversion(self.markdown, 'to_markup') as converter:
            heading = converter(heading, datestamp=False)
        try:
            entry = site[heading]
        except KeyError:
            initial = re.sub(r'.*?(\w).*', r'\1', heading).capitalize()
            entry = Page(heading, site[initial], '', site.leaf_level, None, site.markdown).insert()

        # keep track of which entries have been loaded
        if not self.entries or heading != self.entries[self.current]:
            try:
                self.entries[self.current + 1] = heading
                self.entries = self.entries[:self.current + 2]
            except IndexError:
                self.entries.append(heading)
            self.current += 1

        return entry

    @staticmethod
    def prepare_texts(entry, site, texts, markdown=None, replacelinks=None, kind=None):
        """
        Modify entry with manipulated texts.
        Subroutine of self.save().
        Overrides Editor.prepare_texts()
        :param entry (Page): the entry in the datafile to be modified.
        :param texts (str[]): the texts to be manipulated and inserted.
        :param markdown (Markdown): a Markdown instance to be applied to the texts. If None, the texts are not changed.
        :param return (Nothing):
        """
        text = ''.join(texts)
        # delete and remove page if edit area is empty
        if not text:
            entry.delete_htmlfile()
            entry.remove_from_hierarchy()
        else:
            with ignored(AttributeError):
                text = markdown.to_markup(text)
            with ignored(AttributeError):
                # replace particular words in parts of speech with links to grammar.tinellb.com
                text = replacelinks.replace(text)
            # Write links out in full form
            links = set(re.sub(r'.*?<link>(.*?)</link>.*?', r'\1>', text.replace('\n', '')).split(r'>')[:-1])
            for link in links:
                with ignored(KeyError):
                    lower_link = re.sub(r'^&#x294;', r'&rsquo;', link).lower()
                    text = text.replace('<link>' + link + '</link>', entry.hyperlink(site[lower_link], link))
            # remove duplicate linebreaks
            text = re.sub(r'\n\n+', '\n', text)
            # update datestamp of parent
            entry.parent.content = markdown.to_markup(markdown.to_markdown(entry.parent.content))
        # place text into entry
        entry.content = text

    @staticmethod
    def publish(entry, site):
        """
        Put entry contents into datafile, publish appropriate Pages.
        Overrides Editor.publish()
        Subroutine of self.save()
        """
        if entry.content:
            entry.publish(site.template)
        entry.parent.publish(site.template)
        site.modify_source()
        site.update_json()

if __name__ == '__main__':
    app = DictionaryEditor(directory='c:/users/ryan/documents/tinellbianlanguages/dictionary',
    datafile='data.txt',
    site=Dictionary(),
    markdown=Markdown(
    'c:/users/ryan/documents/tinellbianlanguages/dictionaryreplacements.html'),
    replacelinks=d2gReplace(
    'c:/users/ryan/documents/tinellbianlanguages/dictionarylinkreplacements.txt'),
    randomwords=RandomWords(20,3))
    app.master.title('Dictionary Editor')
    app.mainloop()
