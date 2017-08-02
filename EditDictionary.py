from Edit import *


class EditDictionary(Edit):
    def __init__(self, directory, datafile, site, markdown, replacelinks, randomwords, master=None):
        """
        :param directory (String): the path and filename of the top-level directory
        :param datafile (String): the path, filename and extension of the data file, relative to directory
        :param site (Site): the site being modified
        :param markdown (String): the path, filename and extension of the replacements file, relative to directory
        :param randomwords (int): the number of random words to appear when requested
        """
        self.font = ('Courier New', '15')
        self.widgets = Widgets(1, 1, 'languages')
        Edit.__init__(self, directory, datafile, site, markdown)
        # initialise instance variables
        self.heading = self.headings[0]
        self.edit_text = self.textboxes[0]
        self.entry = ''
        self.page = None
        self.markdown = self.markdowns
        self.site = self.sites
        self.datafile = self.datafiles
        self.words = randomwords.words
        self.replacelinks = replacelinks
        # initialise textboxes and buttons
        self.configure_widgets()

    def configure_widgets(self):
        self.configure_language_radios()
        self.heading.bind('<Control-r>', self.refresh_random)
        self.heading.bind('<Return>', self.load)
        self.edit_text.bind('<Control-n>', self.initial_content)
        self.edit_text.bind('<Control-r>', self.refresh_random)
        self.edit_text.bind('<Control-t>', self.add_translation)
        self.edit_text.bind('<Control-=>', self.add_definition)

    def initial_content(self):
        """
        Insert the appropriate template for a new entry, and move the insertion pointer to allow for immediate input of the pronunciation.
        :precondition: The name of the entry, and its language, are already selected.
        """
        name = self.headings[0].get()
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
    def prepare_entry(entry, markdown=None):
        """
        Manipulate entry content to suit textboxes.
        Subroutine of self.load()
        Overrides method in Edit.py.
        :param entry (Page): A Page instance carrying text. Other Pages relative to this entry may also be accessed.
        :param markdown (Markdown): a Markdown instance to be applied to the contents of the entry. If None, the content is not changed.
        :param return (str[]):
        """
        content = entry.content # for code maintenance: so that next steps can be permuted easily.
        content = markdown.to_markdown(content)
        content = re.sub(r'\\<a href=\\"(?!http).*?\\"\\>(.*?)\\</a\\>', r'<\1>', content)
        content = re.sub(r'\\<a href=\\"http.*?\\"\\>(.*?)\\</a\\>', r'\1', content)
        return [content]

    def find_entry(self, headings):
        """
        Find the current entry based on what is in the heading boxes.
        This is the default method - other Edit programs will override this.
        Subroutine of self.load().
        :param headings (str[]): the texts from the heading boxes
        :return (Page):
        """
        heading = headings[0]
        site = self.sites
        # use str() to suppress unicode string
        heading = self.markdowns.to_markup(heading, datestamp=False)
        try:
            return site[heading]
        except KeyError:
            initial = re.sub(r'.*?(\w).*', r'\1', heading).capitalize()
            return Page(heading, site[initial], '', site.leaf_level, None, site.markdown).insert()

    def save(self, event=None):
        """
        Save the current entry into the output file, and create/update the webpage for itself and its parent.
        :keyboard shortcut: <Ctrl-S>
        """
        # use str() method to suppress unicode string
        self.page.content = str(self.edit_text.get(1.0, Tk.END))
        empty = self.page.content == '\n'
        # delete and remove page if edit area is empty
        if empty:
            self.page.delete()
            self.page.remove()
        else:
            # replace particular words in parts of speech with links to grammar.tinellb.com
            self.page.content = self.replacelinks.replace(self.page.content)
            self.page.content = self.markdown.to_markup(self.page.content)
            # Write links out in full form
            links = set(re.sub(r'.*?<link>(.*?)</link>.*?', r'\1>', self.page.content.replace('\n', '')).split(r'>')[:-1])
            for link in links:
                try:
                    self.page.content = self.page.content.replace('<link>' + link + '</link>', self.page.hyperlink(self.site[link]))
                except KeyError:
                    try:
                        self.page.content = self.page.content.replace('<link>' + link + '</link>', self.page.hyperlink(self.site[self.lowercase(link)], link))
                    except KeyError:
                        pass
            # remove duplicate linebreaks
            self.page.content = re.sub(r'\n\n+', '\n', self.page.content)
            # update datestamp and publish parent.
            parent = self.page.parent
            parent.content = self.markdown.to_markup(self.markdown.to_markdown(parent.content))
            parent.publish(self.site.template)
            self.page.publish(self.site.template)
        page = str(self.site)
        if page:
            with open(self.datafile, 'w') as data:
                data.write(page)
        self.site.update_json()
        self.save_text.set('Save')
        self.edit_text.edit_modified(False)
        return 'break'

    @staticmethod
    def lowercase(text):
        if text.startswith('&#x294'):
            return text.replace('&#x294;', '&rsquo;', 1)
        else:
            return text[0].lower() + text[1:]


if __name__ == '__main__':
    app = EditDictionary(directory='c:/users/ryan/documents/tinellbianlanguages/dictionary',
    datafile='data.txt',
    site=Dictionary(),
    markdown=Markdown(
    'c:/users/ryan/documents/tinellbianlanguages/dictionaryreplacements.html'),
    replacelinks=d2gReplace(
    'c:/users/ryan/documents/tinellbianlanguages/dictionarylinkreplacements.txt'),
    randomwords=RandomWords(20,3))
    app.master.title('Edit the Dictionary')
    app.mainloop()
