import Tkinter as Tk
import os
from Smeagol import *
from Translation import *

class EditDictionary(Tk.Frame):
    def __init__(self, directory, datafile, site, markdown, replacelinks, randomwords, master=None):
        """
        :param directory (String): the path and filename of the top-level directory
        :param datafile (String): the path, filename and extension of the data file, relative to directory
        :param site (Site): the site being modified
        :param markdown (String): the path, filename and extension of the replacements file, relative to directory
        :param randomwords (int): the number of random words to appear when requested
        """
        Tk.Frame.__init__(self, master)
        os.chdir(directory)
        # initialise instance variables
        self.site = site
        self.datafile = datafile
        self.random_word = Tk.StringVar()
        self.language = Tk.StringVar()
        self.entry = ''
        self.page = None
        # initialise other useful classes. Default language is High Lulani
        self.markdown = markdown
        self.translator = Translator('hl')
        self.words = randomwords.words
        self.replacelinks = replacelinks
        # initialise textboxes and buttons
        self.heading = None
        self.go_button = None
        self.save_button = None
        self.save_text = Tk.StringVar()
        self.save_text.set('Save')
        self.edit_text = None
        self.random_words = None
        self.high_lulani = Tk.Radiobutton(self, text='High Lulani', value='hl', variable=self.language, command=self.change_language)
        self.english = Tk.Radiobutton(self, text='English', value='en', variable=self.language, command=self.change_language, anchor=Tk.N)
        self.high_lulani.select()
        # open window
        self.grid()
        self.top = self.winfo_toplevel()
        self.top.state('zoomed')
        self.create_widgets()
        self.heading.focus_set()

    def create_widgets(self):
        self.heading = Tk.Entry(self)
        self.heading.bind('<Control-m>', self.refresh_markdown)
        self.heading.bind('<Control-r>', self.refresh_random)
        self.heading.bind('<Alt-d>', self.go_to_heading)
        self.heading.bind('<Return>', self.load)
        self.go_button = Tk.Button(self, text='Load', command=self.load)
        self.save_button = Tk.Button(self, textvariable=self.save_text, command=self.save)
        self.random_words = Tk.Label(self, textvariable=self.random_word)
        self.edit_text = Tk.Text(self, font=('Courier New', '15'), undo=True, height=31, width=95)
        self.edit_text.bind('<KeyPress>', self.edit_text_changed)
        self.edit_text.bind('<KeyPress-|>', self.insert_pipe)
        self.edit_text.bind('<Control-a>', self.select_all)
        self.edit_text.bind('<Control-b>', self.bold)
        self.edit_text.bind('<Control-i>', self.italic)
        self.edit_text.bind('<Control-k>', self.small_caps)
        self.edit_text.bind('<Control-m>', self.refresh_markdown)
        self.edit_text.bind('<Control-n>', self.new_word)
        self.edit_text.bind('<Control-r>', self.refresh_random)
        self.edit_text.bind('<Control-s>', self.save)
        self.edit_text.bind('<Control-t>', self.add_translation)
        self.edit_text.bind('<Control-=>', self.add_definition)
        self.edit_text.bind('<Control-BackSpace>', self.delete_word)
        self.edit_text.bind('<Alt-d>', self.go_to_heading)
        self.heading.grid(row=0, column=0, columnspan=2, sticky=Tk.N)
        self.go_button.grid(row=1, column=0)
        self.save_button.grid(row=1, column=1)
        self.random_words.grid(row=2, column=0, columnspan=2)
        self.high_lulani.grid(row=3, column=0, columnspan=2)
        self.english.grid(row=4, column=0, columnspan=2)
        self.edit_text.grid(row=0, rowspan=260, column=2)

    @staticmethod
    def insert_characters(textbox, before, after=''):
        """
        Insert given text into a Text textbox, either around an insertion cursor or selected text, and move the cursor to the appropriate place.
        :param textbox (Tkinter Text): The Text into which the given text is to be inserted.
        :param before (str): The text to be inserted before the insertion counter, or before the selected text.
        :param after (str): The text to be inserted after the insertion cursor, or after the selected text.
        """
        try:
            text = textbox.get(Tk.SEL_FIRST, Tk.SEL_LAST)
            textbox.delete(Tk.SEL_FIRST, Tk.SEL_LAST)
            textbox.insert(Tk.INSERT, before + text + after)
        except Tk.TclError:
            textbox.insert(Tk.INSERT, before + after)
            textbox.mark_set(Tk.INSERT, Tk.INSERT + '-{0}c'.format(len(after)))

    def insert_pipe(self, event=None):
        self.insert_characters(self.edit_text, ' | ')
        return 'break'

    def edit_text_changed(self, event=None):
        """
        Notify the user that the edittext has been changed.
        Activates after each keypress.
        Deactivates after a save or a load action.
        """
        if self.edit_text.edit_modified():
            self.save_text.set('*Save')

    def refresh_markdown(self, event=None):
        """
        Reopen replacements file
        """
        self.markdown.refresh()
        self.random_word.set('Markdown Refreshed!')
        return 'break'

    def change_language(self, event=None):
        """
        Change the entry language to whatever is in the StringVar 'self.language'
        """
        self.translator = Translator(self.language.get())
        return 'break'

    def select_all(self, event=None, widget=None):
        """
        Select all the text in the edit area
        """
        try:
            event.widget.tag_add('sel', '1.0', 'end')
        except AttributeError:
            try:
                widget.tag_add('sel', '1.0', 'end')
            except AttributeError:
                pass
        return 'break'

    def delete_word(self, event=None):
        """
        Remove text backwards from the insertion counter to the end of the previous word
        """
        if self.edit_text.get(Tk.INSERT + '-1c') in '.,;:?! ':
            self.edit_text.delete(Tk.INSERT + '-1c wordstart', Tk.INSERT)
        else:
            self.edit_text.delete(Tk.INSERT + '-1c wordstart -1c', Tk.INSERT)
        return 'break'

    def go_to_heading(self, event=None):
        """
        Move focus to the heading textbox, and select all the text therein
        """
        self.heading.focus_set()
        self.heading.select_range(0, 'end')
        return 'break'

    def new_word(self, event=None):
        """
        Insert the appropriate template for a new entry, and move the insertion pointer to allow for immediate input of the pronunciation.
        :precondition: The name of the entry, and its language, are already selected.
        """
        trans = self.translator
        (location, script) = ('4.10', '[4]{0}\n[5][p {1}]//[/p]\n'.format(trans.convert_word(self.entry), trans.code)) if self.language.get() != 'en' else ('3.4', '[5]//\n')
        template = ('2]{0}\n'
                    '[3]{1}\n'
                    '{2}'
                    '[6]\n').format(self.entry, trans.name, script)
        self.edit_text.insert(1.0, template)
        self.edit_text.mark_set(Tk.INSERT, location)
        return 'break'

    def add_definition(self, event=None):
        """
        Insert the markdown for entry definition, and move the insertion pointer to allow for immediate input of the definition.
        """
        self.edit_text.insert(Tk.INSERT, '{{ ==}}')
        self.edit_text.mark_set(Tk.INSERT, Tk.INSERT + '-2c')
        return 'break'

    def refresh_random(self, event=None):
        """
        Show a certain number of random nonsense words using High Lulani phonotactics.
        """
        self.random_word.set('\n'.join(self.words()))
        return 'break'

    def find_formatting(self, keyword):
        """
        Find markdown for specific formatting.
        :param keyword (str): the formatting type, in html, e.g.: strong, em, &c.
        :return (tuple): the opening and closing tags, in markdown, e.g.: ([[, ]]), (<<, >>)
        """
        start = self.markdown.markdown[self.markdown.markup.index('<' + keyword + '>')]
        end = self.markdown.markdown[self.markdown.markup.index('</' + keyword + '>')]
        return start, end

    def insert_tags(self, keyword):
        """
        Insert markdown for specific tags, and place insertion point between them.
        """
        start, end = self.find_formatting(keyword)
        try:
            text = self.edit_text.get(Tk.SEL_FIRST, Tk.SEL_LAST)
            self.edit_text.delete(Tk.SEL_FIRST, Tk.SEL_LAST)
            self.edit_text.insert(Tk.INSERT, start + text + end)
        except Tk.TclError:
            self.edit_text.insert(Tk.INSERT, start + end)
            self.edit_text.mark_set(Tk.INSERT, Tk.INSERT + '-{0}c'.format(len(end)))
        return 'break'

    def bold(self, event=None):
        """
        Insert markdown for bold tags, and place insertion point between them.
        """
        self.insert_tags('strong')
        return 'break'

    def italic(self, event=None):
        """
        Insert markdown for italic tags, and place insertion point between them.
        """
        self.insert_tags('em')
        return 'break'

    def small_caps(self, event=None):
        """
        Insert markdown for small-cap tags, and place insertion point between them.
        """
        self.insert_tags('small-caps')
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

    def load(self, event=None):
        """
        Find the dictionary entry with the same name as the text in the heading box, and place its markedown text within the edit area.
        If such an entry is not found, create one, and insert it into its correct parent folder.
        Replace internal links with the name of the linked entry, surrounded by <>.
        """
        # use str() to suppress unicode string
        self.entry = str(self.heading.get())
        entry = self.markdown.to_markup(self.entry, datestamp=False)
        try:
            self.page = self.site[entry]
        except KeyError:
            initial = re.sub(r'.*?(\w).*', r'\1', self.entry).capitalize()
            self.page = Page(entry, self.site[initial], '', self.site.leaf_level, None, self.site.markdown).insert()
            self.new_word()
        content = self.page.content # for code maintenance: so that next steps can be permuted easily.
        content = self.markdown.to_markdown(content)
        content = re.sub(r'\\<a href=\\"(?!http).*?\\"\\>(.*?)\\</a\\>', r'<\1>', content)
        content = re.sub(r'\\<a href=\\"http.*?\\"\\>(.*?)\\</a\\>', r'\1', content)
        self.edit_text.delete(1.0, Tk.END)
        self.edit_text.insert(1.0, content)
        self.edit_text.focus_set()
        self.edit_text.mark_set(Tk.INSERT, '1.0')
        self.save_text.set('Save')
        self.edit_text.edit_modified(False)
        return 'break'

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
