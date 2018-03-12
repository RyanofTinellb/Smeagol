from site_editor import SiteEditor, Tk, Widgets
from cwsmeagol.site.page import Page
from cwsmeagol.utils import *

class DictionaryEditor(SiteEditor):
    def __init__(self, master=None):
        """

        """
        # initialise instance variables
        self.entry = None
        self.history = []
        self.current = -1

        super(DictionaryEditor, self).__init__(master)
        commands = [
                ('<Control-r>', self.refresh_random),
                ('<Control-=>', self.add_definition),
                ('<Prior>', self.scroll_history),
                ('<Next>', self.scroll_history),
                ('<Control-Prior>', self.previous_entry),
                ('<Control-Next>', self.next_entry),
              ]
        self.widgets.add_commands('Text', commands)
        self.widgets.font.config(family='Courier New')
        self.master.title('Editing Dictionary')

    @property
    def caller(self):
        return 'dictionary'

    def scroll_headings(self, event):
        if event.keysym == 'Prior':
            if self.current > 0:
                self.current -= 1
                self.heading.delete(0, Tk.END)
                self.heading.insert(0, self.properties.markdown.to_markdown(self.history[self.current]))
        elif event.keysym == 'Next':
            if self.current < len(self.history) - 1:
                self.current += 1
                self.heading.delete(0, Tk.END)
                self.heading.insert(0, self.properties.markdown.to_markdown(self.history[self.current]))
        return 'break'

    def scroll_history(self, event):
        self.scroll_headings(event)
        self.load()
        return 'break'

    def previous_entry(self, event):
        self.heading.delete(0, Tk.END)
        self.heading.insert(0, self.entry.previous.name)
        self.load()

    def next_entry(self, event):
        self.heading.delete(0, Tk.END)
        self.heading.insert(0, self.entry.next_node.name)
        self.load()

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
        m = self.properties.markdown.to_markdown
        self.insert_characters(widget, m('<div class="definition">'), m('</div>'))
        return 'break'

    def find_entry(self, headings):
        """
        Find the current entry based on what is in the heading boxes.
        Overrides SiteEditor.find_entry.
        Subroutine of self.load().
        :param headings (str[]): the texts from the heading boxes
        :return (Page):
        """
        heading = headings[0]
        site = self.properties.site
        with conversion(self.properties.markdown, 'to_markup') as converter:
            heading = converter(heading)
        try:
            entry = site[heading]
        except KeyError:
            initial = re.sub(r'.*?(\w).*', r'\1', urlform(heading)).capitalize()
            entry = Page(heading, site[initial], '').insert()
            entry.content = self.initial_content(entry)
        self.keep_history(heading)
        self.master.title('Editing Dictionary: ' + self.entry.name)
        return entry

    def prepare_texts(self, texts):
        """
        Modify entry with manipulated texts.
        Subroutine of self.save().
        Overrides SiteEditor.prepare_texts()
        :param entry (Page): the entry in the datafile to be modified.
        :param texts (str[]): the texts to be manipulated and inserted.
        :param markdown (Markdown): a Markdown instance to be applied to the texts. If None, the texts are not changed.
        :param return (Nothing):
        """
        texts = super(DictionaryEditor, self).prepare_texts(texts)
        with ignored(AttributeError):
            self.entry.parent.content = replace_datestamp(self.entry.parent.content)

    @staticmethod
    def publish(entry, site, allpages=False):
        """
        Put entry contents into datafile, publish appropriate Pages.
        Overrides SiteEditor.publish()
        Subroutine of self.save()
        """
        if entry.content:
            entry.publish(site.template)
        with ignored(AttributeError):
            entry.parent.publish(site.template)
        site.modify_source()
        site.update_json()

    def initial_content(self, entry=None):
        """
        Return the content to be placed in a textbox if the page is new
        """
        if entry is None:
            entry = self.entry
        name = entry.name
        trans = self.translator
        before = ('[1]{0}\n[2]{1}\n').format(name, trans.name)
        before += '' if self.language.get() == 'en' else '[3]{0}\n'.format(trans.convert_word(name))
        before += '[4][p {0}]/'.format(trans.code)
        after = '/[/p]\n[5]\n'
        return before + after

    @property
    def heading_commands(self):
        commands = super(DictionaryEditor, self).heading_commands
        commands += [(['<Control-r>'], self.refresh_random)]
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
