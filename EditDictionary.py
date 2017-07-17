import Tkinter as Tk
import os
import threading
from Smeagol import *
from Translation import *


class EditDictionary(Tk.Frame):
    def __init__(self, dir, outputfile, site, searchfile, master=None,):
        """
        :param dir (String): the path and filename of the top-level directory
        :param outputfile (String): the path, filename and extension of the output file, relative to dir
        :param site (Site): the site being modified
        :param searchfile (String): the path, filename and extension of the file wherein the json text for site searches will be placed, relative to dir
        """
        Tk.Frame.__init__(self, master)
        os.chdir(dir)
        # initialise instance variables
        self.site = site
        self.outputfile = outputfile
        self.searchfile = searchfile
        self.random_word = Tk.StringVar()
        self.language = Tk.StringVar()
        self.entry = ''
        self.page = None
        # initialise other useful classes. Default language is High Lulani
        self.markdown = Markdown()
        self.translator = Translator('hl')
        # initialise textboxes and buttons
        self.heading = None
        self.go_button = None
        self.publish_button = None
        self.edit_text = None
        self.random_words = None
        self.high_lulani = Tk.Radiobutton(self, text='High Lulani', value='hl', variable=self.language,
                                          command=self.change_language)
        self.english = Tk.Radiobutton(self, text='English', value='en', variable=self.language,
                                      command=self.change_language, anchor=Tk.N)
        self.high_lulani.select()
        # open window
        self.grid()
        self.top = self.winfo_toplevel()
        self.top.state('zoomed')
        self.create_widgets()
        self.heading.focus_set()

    def create_widgets(self):
        self.heading = Tk.Text(self, height=1, width=20, wrap=Tk.NONE)
        self.heading.grid(sticky=Tk.NE)
        self.heading.bind('<Control-r>', self.refresh_random)
        self.heading.bind('<Alt-d>', self.go_to_heading)
        self.heading.bind('<Return>', self.bring_entry)
        self.go_button = Tk.Button(self, text='GO!', command=self.bring_entry)
        self.go_button.grid(row=1, column=1, sticky=Tk.NW)
        self.publish_button = Tk.Button(text='Publish', command=self.save)
        self.publish_button.grid(row=1, column=2, sticky=Tk.NW)
        self.random_words = Tk.Label(self, textvariable=self.random_word)
        self.random_words.grid(row=1, column=0)
        self.edit_text = Tk.Text(self, height=27, width=88, font=('Courier New', '15'))
        self.edit_text.bind('<Control-a>', self.select_all)
        self.edit_text.bind('<Control-b>', self.bold)
        self.edit_text.bind('<Control-i>', self.italic)
        self.edit_text.bind('<Control-k>', self.small_caps)
        self.edit_text.bind('<Control-n>', self.new_word)
        self.edit_text.bind('<Control-r>', self.refresh_random)
        self.edit_text.bind('<Control-s>', self.save)
        self.edit_text.bind('<Control-t>', self.add_translation)
        self.edit_text.bind('<Control-z>', self.bring_entry)
        self.edit_text.bind('<Control-=>', self.add_definition)
        self.edit_text.bind('<Control-BackSpace>', self.delete_word)
        self.edit_text.bind('<Alt-d>', self.go_to_heading)
        self.edit_text.grid(row=1, rowspan=200, column=1)
        self.high_lulani.grid(row=2, column=0)
        self.english.grid(row=3, column=0)

    def change_language(self, event=None):
        """
        Change the entry language to whatever is in the StringVar 'self.language'
        """
        self.translator = Translator(self.language.get())

    def select_all(self, event=None):
        """
        Select all the text in the edit area
        """
        self.edit_text.tag_add('sel', '1.0', 'end')
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
        self.heading.tag_add('sel', '1.0', 'end-1c')
        return 'break'

    def new_word(self, event=None):
        """
        Insert the appropriate template for a new entry, and move the insertion pointer to allow for immediate input of the pronunciation.
        :precondition: The name of the entry, and its language, are already selected.
        """
        trans = self.translator
        (location, script) = ('4.7', '[4]{0}\n'.format(trans.convert_word(self.entry))) if self.language.get() != 'en' else ('3.7', '')
        template = ('2]{0}\n'
                    '[3]{1}\n'
                    '{2}'
                    '[5][p]//[/p]\n'
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
        number = 20
        text = '\n'.join(Translation.make_words(number))
        self.random_word.set(text)
        return 'break'

    def bold(self, event=None):
        """
        Insert markdown for bold tags, and place insertion point between them.
        """
        self.edit_text.insert(Tk.INSERT, '[b][/b]')
        self.edit_text.mark_set(Tk.INSERT, Tk.INSERT + '-4c')
        return 'break'

    def italic(self, event=None):
        """
        Insert markdown for italic tags, and place insertion point between them.
        """
        self.edit_text.insert(Tk.INSERT, '[i][/i]')
        self.edit_text.mark_set(Tk.INSERT, Tk.INSERT + '-4c')
        return 'break'

    def small_caps(self, event=None):
        """
        Insert markdown for small-cap tags, and place insertion point between them.
        """
        self.edit_text.insert(Tk.INSERT, '[k][/k]')
        self.edit_text.mark_set(Tk.INSERT, Tk.INSERT + '-4c')
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

    def collapse_table(self, event):
        text = self.edit_text.get(Tk.SEL_FIRST, Tk.SEL_LAST)
        text = text.replace('\n', ' | ')
        text = text.replace(' | [r]', '\n[r]')
        self.edit_text.delete(Tk.SEL_FIRST, Tk.SEL_LAST)
        self.edit_text.insert(Tk.INSERT, text)
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


    def bring_entry(self, event=None):
        """
        Find the dictionary entry with the same name as the text in the heading box, and place its markedown text within the edit area.
        If such an entry is not found, create one, and insert it into its correct parent folder.
        Replace internal links with the name of the linked entry, surrounded by <>.
        """
        self.markdown = Markdown()
        self.entry = str(self.heading.get(1.0, Tk.END + "-1c"))
        entry = self.markdown.to_markup(self.entry)
        try:
            self.page = self.site[entry]
        except KeyError:
            initial = re.sub(r'.*?(\w).*', r'\1', self.entry).capitalize()
            self.page = Page(entry, self.site[initial], '', self.site.leaf_level).insert()
            self.new_word()
        content = re.sub(r'<a href="(?<!=http).*?">(.*?)</a>', r'{\1}', self.page.content)
        content = self.markdown.to_markdown(content)
        self.edit_text.delete(1.0, Tk.END)
        self.edit_text.insert(1.0, content)
        self.edit_text.focus_set()
        self.edit_text.mark_set(Tk.INSERT, '1.0')
        return 'break'

    def save(self, event=None):
        self.is_bold = self.is_italic = self.is_small_caps = False
        self.page.content = self.markdown.to_markup(str(self.edit_text.get(1.0, Tk.END)))
        links = set(re.sub(r'.*?{(.*?)}.*?', r'\1}', self.page.content.replace('\n', '')).split(r'}')[:-1])
        """
        Save the current entry into the output file, and create/update the webpage for itself and its parent.
        """
        for link in links:
            try:
                hyperlink = self.page.hyperlink(self.dictionary[link])
            except KeyError:
                hyperlink = link
            self.page.content = self.page.content.replace('{' + link + '}', hyperlink)
        while self.page.content[-2:] == "\n\n":
            self.page.content = self.page.content[:-1]
        if self.page.content == '\n':
            self.page.delete()
            self.page.remove()
        else:
            self.page.publish()
        page = str(self.site)
        if page:
            with open(self.outputfile, 'w') as data:
                data.write(page)
        page = str(self.dictionary.analyse())
        if page:
                data.write(page)
        text = str(self.site.analyse())
        if text:
            with open(self.searchfile, 'w') as data:
                data.write(text)
        return 'break'

app = EditDictionary(dir='C:/Users/Ryan/Documents/TinellbianLanguages/dictionary',
                    outputfile='data.txt',
                    site=Dictionary(),
                    searchfile='searching.json')
app.master.title('Edit the Dictionary')
app.mainloop()
