from editor import Editor, WidgetAmounts
from cwsmeagol.utils import *

class DictionaryEditor(Editor):
    def __init__(self, site=None, markdown=None, links=None, randomwords=None, master=None):
        """
        :param directory (String): the path and filename of the top-level directory
        :param datafile (String): the path, filename and extension of the data file, relative to directory
        :param site (Site): the site being modified
        :param markdown (String): the path, filename and extension of the replacements file, relative to directory
        :param randomwords (int): the number of random words to appear when requested
        """
        font = ('Courier New', '15')
        widgets = WidgetAmounts(headings=1, textboxes=1, radios='languages')
        super(DictionaryEditor, self).__init__(properties, widgets, font)

        # initialise instance variables
        self.entry, self.history, self.current, self.page = '', [], -1, None

    def configure_widgets(self):
        self.words = self.randomwords.words
        super(DictionaryEditor, self).configure_widgets()


    def scroll_headings(self, event):
        if event.keysym == 'Prior':
            if self.current > 0:
                self.current -= 1
                self.heading.delete(0, Tk.END)
                self.heading.insert(0, self.markdown.to_markdown(self.history[self.current]))
        elif event.keysym == 'Next':
            if self.current < len(self.history) - 1:
                self.current += 1
                self.heading.delete(0, Tk.END)
                self.heading.insert(0, self.markdown.to_markdown(self.history[self.current]))
        return 'break'

    def scroll_history(self, event):
        self.scroll_headings(event)
        self.load()
        return 'break'

    def keep_history(self, heading):
        """
        Keep track of which entries have been loaded
        """
        if not self.history or heading != self.history[self.current]:
            try:
                self.history[self.current + 1] = heading
                self.history = self.history[:self.current + 2]
            except IndexError:
                self.history.append(heading)
            self.current += 1

    def add_definition(self, event=None):
        """
        Insert the markdown for entry definition, and move the insertion pointer to allow for immediate input of the definition.
        """
        widget = event.widget
        self.insert_characters(widget, *self.markdown.find_formatting('div'))
        self.insert_characters(widget, ' ' + self.markdown.find('class="definition">'))
        return 'break'

    def add_translation(self, event=None):
        """
        Insert a transliteration of the selected text in the current language.
        Do sentence conversion if there is a period in the text, and word conversion otherwise.
        Insert an additional linebreak if the selection ends with a linebreak.
        """
        try:
            text = self.textbox.get(Tk.SEL_FIRST, Tk.SEL_LAST)
        except Tk.TclError:
            text = self.textbox.get(Tk.INSERT + ' wordstart', Tk.INSERT + ' wordend')
        converter = self.translator.convert_sentence if '.' in text else self.translator.convert_word
        text = converter(text)
        try:
            text += '\n' if self.textbox.compare(Tk.SEL_LAST, '==', Tk.SEL_LAST + ' lineend') else ' '
            self.textbox.insert(Tk.SEL_LAST + '+1c', text)
        except Tk.TclError:
            text += ' '
            self.textbox.mark_set(Tk.INSERT, Tk.INSERT + ' wordend')
            self.textbox.insert(Tk.INSERT + '+1c', text)
        self.textbox.mark_set(Tk.INSERT, '{0}+{1}c'.format(Tk.INSERT, str(len(text) + 1)))
        return 'break'

    def find_entry(self, headings):
        """
        Find the current entry based on what is in the heading boxes.
        Overrides Editor.find_entry.
        Subroutine of self.load().
        :param headings (str[]): the texts from the heading boxes
        :return (Page):
        """
        heading = headings[0]
        site = self.site
        with conversion(self.markdown, 'to_markup') as converter:
            heading = converter(heading)
        try:
            entry = site[heading]
        except KeyError:
            initial = re.sub(r'.*?(\w).*', r'\1', urlform(heading, self.site.markdown)).capitalize()
            entry = Page(heading, site[initial], '', site.leaf_level, None, site.markdown).insert()
        self.keep_history(heading)
        return entry

    def prepare_texts(self, texts):
        """
        Modify entry with manipulated texts.
        Subroutine of self.save().
        Overrides Editor.prepare_texts()
        :param entry (Page): the entry in the datafile to be modified.
        :param texts (str[]): the texts to be manipulated and inserted.
        :param markdown (Markdown): a Markdown instance to be applied to the texts. If None, the texts are not changed.
        :param return (Nothing):
        """
        texts = super(DictionaryEditor, self).prepare_texts(texts)
        with ignored(AttributeError):
            self.entry.parent.content = replace_datestamp(self.entry.parent.content)

    @staticmethod
    def publish(entry, site):
        """
        Put entry contents into datafile, publish appropriate Pages.
        Overrides Editor.publish()
        Subroutine of self.save()
        """
        if entry.content:
            entry.publish(site.template)
        with ignored(AttributeError):
            entry.parent.publish(site.template)
        site.modify_source()
        site.update_json()

    @property
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

    @property
    def heading_commands(self):
        commands = super(DictionaryEditor, self).heading_commands
        commands += [(['<Control-r>'], self.refresh_random)]
        return commands

    @property
    def textbox_commands(self):
        commands = super(DictionaryEditor, self).textbox_commands
        commands += [
        ('<Control-r>', self.refresh_random),
        ('<Control-t>', self.add_translation),
        ('<Control-=>', self.add_definition),
        ('<Prior>', self.scroll_history),
        ('<Next>', self.scroll_history)]
        return commands


if __name__ == '__main__':
    links = [ExternalGrammar('c:/users/ryan/documents/'
            'tinellbianlanguages/dictionarylinks.txt'),
            InternalDictionary()]
    app = DictionaryEditor(site=Dictionary(),
    markdown=Markdown('c:/users/ryan/documents/'
        'tinellbianlanguages/dictionaryreplacements.mkd'),
    links=AddRemoveLinks(links),
    randomwords=RandomWords(20,3))
    app.master.title('Dictionary Editor')
    app.mainloop()
